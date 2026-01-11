"""비디오에서 오디오를 추출하는 유틸리티"""
import os
import tempfile
from pathlib import Path
from typing import Optional, List
import yt_dlp
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


class AudioExtractor:
    def __init__(self, temp_dir: str = "./temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    async def download_video(self, url: str) -> Optional[str]:
        """
        비디오 URL에서 비디오 다운로드
        인스타그램, 틱톡 등 다양한 플랫폼 지원
        """
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                logger.info(f"비디오 다운로드 완료: {video_path}")
                return video_path

        except Exception as e:
            logger.error(f"비디오 다운로드 실패: {str(e)}")
            return None

    async def extract_audio(self, video_path: str, output_format: str = "mp3") -> Optional[str]:
        """
        비디오 파일에서 오디오 추출
        """
        try:
            video = AudioSegment.from_file(video_path)

            # 출력 파일 경로
            audio_path = str(self.temp_dir / f"{Path(video_path).stem}.{output_format}")

            # 오디오 추출 및 저장
            video.export(audio_path, format=output_format)
            logger.info(f"오디오 추출 완료: {audio_path}")

            return audio_path

        except Exception as e:
            logger.error(f"오디오 추출 실패: {str(e)}")
            return None

    async def split_audio_segments(
        self,
        audio_path: str,
        segment_duration_sec: int = 10,
        overlap_sec: int = 2
    ) -> List[str]:
        """
        오디오를 여러 세그먼트로 분할
        여러 노래를 감지하기 위해 오디오를 겹치는 세그먼트로 분할

        Args:
            audio_path: 오디오 파일 경로
            segment_duration_sec: 각 세그먼트 길이 (초)
            overlap_sec: 세그먼트 간 겹침 (초)

        Returns:
            세그먼트 파일 경로 리스트
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            total_duration_ms = len(audio)
            segment_duration_ms = segment_duration_sec * 1000
            overlap_ms = overlap_sec * 1000

            segments = []
            start_ms = 0

            segment_num = 0
            while start_ms < total_duration_ms:
                end_ms = min(start_ms + segment_duration_ms, total_duration_ms)

                # 세그먼트 추출
                segment = audio[start_ms:end_ms]

                # 세그먼트 저장
                segment_path = str(
                    self.temp_dir / f"{Path(audio_path).stem}_segment_{segment_num}.mp3"
                )
                segment.export(segment_path, format="mp3")
                segments.append(segment_path)

                logger.info(
                    f"세그먼트 생성: {segment_num} "
                    f"({start_ms/1000:.1f}s - {end_ms/1000:.1f}s)"
                )

                # 다음 세그먼트 시작 위치 (겹침 고려)
                start_ms += segment_duration_ms - overlap_ms
                segment_num += 1

            logger.info(f"총 {len(segments)}개 세그먼트 생성")
            return segments

        except Exception as e:
            logger.error(f"오디오 세그먼트 분할 실패: {str(e)}")
            return []

    async def process_video_url(
        self,
        url: str,
        create_segments: bool = True
    ) -> dict:
        """
        비디오 URL을 처리하여 오디오 파일(들) 생성

        Returns:
            {
                'audio_path': str,  # 전체 오디오 파일
                'segments': List[str],  # 세그먼트 파일들 (create_segments=True인 경우)
                'duration_sec': float,  # 오디오 길이
            }
        """
        # 비디오 다운로드
        video_path = await self.download_video(url)
        if not video_path:
            raise Exception("비디오 다운로드 실패")

        # 오디오 추출
        audio_path = await self.extract_audio(video_path)
        if not audio_path:
            # 비디오 파일 삭제
            os.remove(video_path)
            raise Exception("오디오 추출 실패")

        # 오디오 길이 확인
        audio = AudioSegment.from_file(audio_path)
        duration_sec = len(audio) / 1000.0

        result = {
            'audio_path': audio_path,
            'video_path': video_path,
            'duration_sec': duration_sec,
            'segments': []
        }

        # 세그먼트 생성
        if create_segments:
            segments = await self.split_audio_segments(audio_path)
            result['segments'] = segments

        return result

    def cleanup(self, *file_paths: str):
        """임시 파일 삭제"""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"파일 삭제: {file_path}")
            except Exception as e:
                logger.error(f"파일 삭제 실패 {file_path}: {str(e)}")

    def cleanup_all(self):
        """temp 디렉토리의 모든 파일 삭제"""
        try:
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            logger.info("모든 임시 파일 삭제 완료")
        except Exception as e:
            logger.error(f"임시 파일 삭제 실패: {str(e)}")
