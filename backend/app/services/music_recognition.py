"""음악 감지 서비스 통합"""
import asyncio
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from shazamio import Shazam
import acoustid
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class SongMatch:
    """감지된 노래 정보"""
    title: str
    artist: str
    album: Optional[str] = None
    release_date: Optional[str] = None
    confidence: float = 0.0
    service: str = ""
    isrc: Optional[str] = None
    spotify_id: Optional[str] = None
    apple_music_id: Optional[str] = None
    genre: Optional[str] = None
    duration_ms: Optional[int] = None
    raw_data: Optional[dict] = None


class ShazamRecognizer:
    """Shazam 음악 감지 (shazamio 라이브러리 사용)"""

    def __init__(self):
        self.shazam = Shazam()

    async def recognize(self, audio_path: str) -> Optional[SongMatch]:
        """오디오 파일에서 노래 감지"""
        try:
            # Shazam으로 음악 감지
            result = await self.shazam.recognize_song(audio_path)

            if not result or 'track' not in result:
                logger.warning("Shazam: 노래를 찾을 수 없습니다")
                return None

            track = result['track']

            # 결과 파싱
            song = SongMatch(
                title=track.get('title', 'Unknown'),
                artist=track.get('subtitle', 'Unknown'),
                album=track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text') if track.get('sections') else None,
                service="shazam",
                confidence=0.9,  # Shazam은 신뢰도 점수를 제공하지 않으므로 기본값
                isrc=track.get('isrc'),
                raw_data=track
            )

            # Spotify/Apple Music ID 추출
            if 'hub' in track and 'providers' in track['hub']:
                for provider in track['hub']['providers']:
                    if provider.get('type') == 'spotify':
                        song.spotify_id = provider.get('actions', [{}])[0].get('uri', '').split(':')[-1]
                    elif provider.get('type') == 'applemusic':
                        song.apple_music_id = provider.get('actions', [{}])[0].get('id')

            logger.info(f"Shazam 감지 성공: {song.title} - {song.artist}")
            return song

        except Exception as e:
            logger.error(f"Shazam 감지 실패: {str(e)}")
            return None


class AcoustIDRecognizer:
    """AcoustID 음악 감지 (무료, 오픈소스)"""

    def __init__(self, api_key: str = "8XaBELgH"):
        # 공개 테스트 키, 프로덕션에서는 자체 키 발급 필요
        self.api_key = api_key

    async def recognize(self, audio_path: str) -> Optional[SongMatch]:
        """오디오 파일에서 노래 감지"""
        try:
            # AcoustID로 fingerprint 생성 및 조회
            duration, fingerprint = acoustid.fingerprint_file(audio_path)

            # MusicBrainz에서 메타데이터 조회
            results = acoustid.lookup(
                apikey=self.api_key,
                fingerprint=fingerprint,
                duration=duration,
                meta='recordings releases'
            )

            # 가장 높은 점수의 결과 선택
            if not results or 'results' not in results or len(results['results']) == 0:
                logger.warning("AcoustID: 노래를 찾을 수 없습니다")
                return None

            best_match = None
            best_score = 0

            for result in results['results']:
                score = result.get('score', 0)
                if score > best_score and 'recordings' in result:
                    best_score = score
                    best_match = result

            if not best_match:
                return None

            recording = best_match['recordings'][0]
            release = recording.get('releases', [{}])[0] if 'releases' in recording else {}

            song = SongMatch(
                title=recording.get('title', 'Unknown'),
                artist=recording.get('artists', [{}])[0].get('name', 'Unknown'),
                album=release.get('title'),
                release_date=release.get('date'),
                confidence=best_score,
                service="acoustid",
                duration_ms=recording.get('duration', 0) * 1000 if recording.get('duration') else None,
                raw_data=best_match
            )

            logger.info(f"AcoustID 감지 성공: {song.title} - {song.artist} (score: {best_score})")
            return song

        except Exception as e:
            logger.error(f"AcoustID 감지 실패: {str(e)}")
            return None


class AuddRecognizer:
    """Audd.io 음악 감지 (무료 플랜: 1000 requests/month)"""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("AUDD_API_TOKEN")
        self.api_url = "https://api.audd.io/"

    async def recognize(self, audio_path: str) -> Optional[SongMatch]:
        """오디오 파일에서 노래 감지"""
        if not self.api_token:
            logger.warning("Audd.io API 토큰이 설정되지 않았습니다")
            return None

        try:
            # 파일 업로드하여 감지
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                data = {'api_token': self.api_token, 'return': 'spotify,apple_music'}

                response = requests.post(self.api_url, files=files, data=data, timeout=30)
                result = response.json()

            if result.get('status') != 'success' or not result.get('result'):
                logger.warning("Audd.io: 노래를 찾을 수 없습니다")
                return None

            track = result['result']

            song = SongMatch(
                title=track.get('title', 'Unknown'),
                artist=track.get('artist', 'Unknown'),
                album=track.get('album'),
                release_date=track.get('release_date'),
                service="audd",
                confidence=0.85,  # Audd는 신뢰도를 제공하지 않으므로 기본값
                spotify_id=track.get('spotify', {}).get('id'),
                apple_music_id=track.get('apple_music', {}).get('id'),
                raw_data=track
            )

            logger.info(f"Audd.io 감지 성공: {song.title} - {song.artist}")
            return song

        except Exception as e:
            logger.error(f"Audd.io 감지 실패: {str(e)}")
            return None


class MusicRecognitionService:
    """
    여러 음악 감지 서비스를 통합하여 정확도를 높이는 서비스
    """

    def __init__(self):
        self.shazam = ShazamRecognizer()
        self.acoustid = AcoustIDRecognizer()
        self.audd = AuddRecognizer()

    async def recognize_single(
        self,
        audio_path: str,
        services: List[str] = None
    ) -> List[SongMatch]:
        """
        단일 오디오 파일에서 노래 감지
        여러 서비스를 병렬로 실행하여 결과 수집

        Args:
            audio_path: 오디오 파일 경로
            services: 사용할 서비스 목록 (기본: 모두)

        Returns:
            감지된 노래 목록 (서비스별)
        """
        if services is None:
            services = ['shazam', 'acoustid', 'audd']

        tasks = []

        if 'shazam' in services:
            tasks.append(self.shazam.recognize(audio_path))
        if 'acoustid' in services:
            tasks.append(self.acoustid.recognize(audio_path))
        if 'audd' in services:
            tasks.append(self.audd.recognize(audio_path))

        # 모든 서비스 병렬 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 유효한 결과만 필터링
        songs = []
        for result in results:
            if isinstance(result, SongMatch):
                songs.append(result)
            elif isinstance(result, Exception):
                logger.error(f"서비스 실행 중 오류: {str(result)}")

        return songs

    async def recognize_multiple_segments(
        self,
        segment_paths: List[str],
        services: List[str] = None
    ) -> Dict[str, List[SongMatch]]:
        """
        여러 오디오 세그먼트에서 노래 감지
        한 영상에 여러 노래가 있을 수 있으므로 각 세그먼트를 개별 감지

        Args:
            segment_paths: 오디오 세그먼트 파일 경로 리스트
            services: 사용할 서비스 목록

        Returns:
            세그먼트별 감지 결과 딕셔너리
        """
        results = {}

        for idx, segment_path in enumerate(segment_paths):
            logger.info(f"세그먼트 {idx + 1}/{len(segment_paths)} 처리 중...")
            songs = await self.recognize_single(segment_path, services)
            results[f"segment_{idx}"] = songs

            # API 제한 방지를 위한 딜레이
            if idx < len(segment_paths) - 1:
                await asyncio.sleep(1)

        return results

    def deduplicate_songs(self, all_songs: List[SongMatch]) -> List[SongMatch]:
        """
        중복 제거 및 최고 신뢰도 선택

        여러 세그먼트에서 같은 노래가 감지될 수 있으므로
        제목과 아티스트가 유사한 경우 하나로 통합
        """
        unique_songs = {}

        for song in all_songs:
            # 정규화된 키 생성 (소문자, 공백 제거)
            key = f"{song.title.lower().strip()}_{song.artist.lower().strip()}"

            if key not in unique_songs:
                unique_songs[key] = song
            else:
                # 신뢰도가 더 높은 것 선택
                if song.confidence > unique_songs[key].confidence:
                    unique_songs[key] = song

        return list(unique_songs.values())

    def merge_results_from_services(self, songs: List[SongMatch]) -> Optional[SongMatch]:
        """
        여러 서비스의 결과를 하나로 통합
        가장 신뢰도가 높은 결과를 기본으로 하고, 부족한 정보를 다른 결과에서 보완
        """
        if not songs:
            return None

        # 신뢰도순 정렬
        songs.sort(key=lambda s: s.confidence, reverse=True)
        best = songs[0]

        # 다른 결과에서 누락된 정보 보완
        for song in songs[1:]:
            if not best.album and song.album:
                best.album = song.album
            if not best.release_date and song.release_date:
                best.release_date = song.release_date
            if not best.spotify_id and song.spotify_id:
                best.spotify_id = song.spotify_id
            if not best.apple_music_id and song.apple_music_id:
                best.apple_music_id = song.apple_music_id
            if not best.isrc and song.isrc:
                best.isrc = song.isrc

        return best

    async def process_video(
        self,
        audio_path: str,
        segment_paths: List[str] = None,
        services: List[str] = None
    ) -> List[SongMatch]:
        """
        비디오 전체 처리하여 모든 노래 감지

        Args:
            audio_path: 전체 오디오 파일 경로
            segment_paths: 세그먼트 파일 경로 리스트 (옵션)
            services: 사용할 서비스 목록

        Returns:
            감지된 모든 고유 노래 리스트
        """
        all_songs = []

        # 전체 오디오 감지
        logger.info("전체 오디오 감지 중...")
        full_audio_songs = await self.recognize_single(audio_path, services)

        # 각 서비스 결과를 통합
        if full_audio_songs:
            merged_song = self.merge_results_from_services(full_audio_songs)
            if merged_song:
                all_songs.append(merged_song)

        # 세그먼트별 감지 (여러 노래 감지)
        if segment_paths:
            logger.info(f"{len(segment_paths)}개 세그먼트 감지 중...")
            segment_results = await self.recognize_multiple_segments(segment_paths, services)

            for segment_name, songs in segment_results.items():
                if songs:
                    merged = self.merge_results_from_services(songs)
                    if merged:
                        all_songs.append(merged)

        # 중복 제거
        unique_songs = self.deduplicate_songs(all_songs)

        logger.info(f"총 {len(unique_songs)}개 고유 노래 감지 완료")
        return unique_songs
