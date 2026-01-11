"""API 라우트"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from ..models.database import DetectedSong, VideoProcessingJob, get_session
from ..services.music_recognition import MusicRecognitionService, SongMatch
from ..utils.audio_extractor import AudioExtractor
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# 서비스 인스턴스
music_service = MusicRecognitionService()
audio_extractor = AudioExtractor()


class VideoSubmitRequest(BaseModel):
    """비디오 제출 요청"""
    url: str
    platform: str = "unknown"  # instagram, tiktok, youtube, etc.
    services: Optional[List[str]] = None  # 사용할 감지 서비스


class VideoSubmitResponse(BaseModel):
    """비디오 제출 응답"""
    job_id: int
    status: str
    message: str


class SongResponse(BaseModel):
    """노래 정보 응답"""
    id: int
    title: str
    artist: str
    album: Optional[str]
    release_date: Optional[str]
    service: str
    confidence: float
    spotify_id: Optional[str]
    apple_music_id: Optional[str]
    isrc: Optional[str]
    detected_at: datetime


class JobStatusResponse(BaseModel):
    """작업 상태 응답"""
    job_id: int
    status: str
    progress: int
    songs_detected: int
    error_message: Optional[str]
    songs: List[SongResponse]


async def process_video_background(
    job_id: int,
    video_url: str,
    services: Optional[List[str]],
    db: AsyncSession
):
    """백그라운드에서 비디오 처리"""
    try:
        # 작업 상태 업데이트: processing
        job = await db.get(VideoProcessingJob, job_id)
        job.status = "processing"
        job.progress = 10
        await db.commit()

        # 1. 비디오에서 오디오 추출
        logger.info(f"[Job {job_id}] 비디오 처리 시작: {video_url}")
        audio_data = await audio_extractor.process_video_url(video_url, create_segments=True)

        job.progress = 30
        await db.commit()

        # 2. 음악 감지
        logger.info(f"[Job {job_id}] 음악 감지 시작")
        detected_songs = await music_service.process_video(
            audio_path=audio_data['audio_path'],
            segment_paths=audio_data['segments'],
            services=services
        )

        job.progress = 80
        await db.commit()

        # 3. 데이터베이스에 저장
        logger.info(f"[Job {job_id}] {len(detected_songs)}개 노래 저장 중")
        for song in detected_songs:
            db_song = DetectedSong(
                title=song.title,
                artist=song.artist,
                album=song.album,
                release_date=song.release_date,
                detection_service=song.service,
                confidence=song.confidence,
                video_url=video_url,
                video_platform=job.platform,
                isrc=song.isrc,
                spotify_id=song.spotify_id,
                apple_music_id=song.apple_music_id,
                genre=song.genre,
                duration_ms=song.duration_ms,
                raw_response=json.dumps(song.raw_data) if song.raw_data else None
            )
            db.add(db_song)

        # 4. 작업 완료
        job.status = "completed"
        job.progress = 100
        job.songs_detected = len(detected_songs)
        job.completed_at = datetime.utcnow()
        await db.commit()

        logger.info(f"[Job {job_id}] 처리 완료: {len(detected_songs)}개 노래 감지")

        # 5. 임시 파일 정리
        audio_extractor.cleanup(
            audio_data['audio_path'],
            audio_data['video_path'],
            *audio_data['segments']
        )

    except Exception as e:
        logger.error(f"[Job {job_id}] 처리 실패: {str(e)}", exc_info=True)

        # 작업 실패 처리
        job = await db.get(VideoProcessingJob, job_id)
        job.status = "failed"
        job.error_message = str(e)
        await db.commit()


@router.post("/submit", response_model=VideoSubmitResponse)
async def submit_video(
    request: VideoSubmitRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """
    비디오 URL 제출하여 음악 감지 시작
    """
    try:
        # 작업 생성
        job = VideoProcessingJob(
            video_url=request.url,
            platform=request.platform,
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # 백그라운드 태스크로 처리
        background_tasks.add_task(
            process_video_background,
            job.id,
            request.url,
            request.services,
            db
        )

        return VideoSubmitResponse(
            job_id=job.id,
            status="pending",
            message="비디오 처리가 시작되었습니다"
        )

    except Exception as e:
        logger.error(f"비디오 제출 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    작업 상태 조회
    """
    job = await db.get(VideoProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

    # 해당 작업의 노래 조회
    stmt = select(DetectedSong).where(DetectedSong.video_url == job.video_url)
    result = await db.execute(stmt)
    songs = result.scalars().all()

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        songs_detected=job.songs_detected,
        error_message=job.error_message,
        songs=[
            SongResponse(
                id=song.id,
                title=song.title,
                artist=song.artist,
                album=song.album,
                release_date=song.release_date,
                service=song.detection_service,
                confidence=song.confidence,
                spotify_id=song.spotify_id,
                apple_music_id=song.apple_music_id,
                isrc=song.isrc,
                detected_at=song.detected_at
            )
            for song in songs
        ]
    )


@router.get("/songs", response_model=List[SongResponse])
async def get_all_songs(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session)
):
    """
    저장된 모든 노래 조회
    """
    stmt = select(DetectedSong).order_by(DetectedSong.detected_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    songs = result.scalars().all()

    return [
        SongResponse(
            id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            release_date=song.release_date,
            service=song.detection_service,
            confidence=song.confidence,
            spotify_id=song.spotify_id,
            apple_music_id=song.apple_music_id,
            isrc=song.isrc,
            detected_at=song.detected_at
        )
        for song in songs
    ]


@router.delete("/song/{song_id}")
async def delete_song(
    song_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    노래 삭제
    """
    song = await db.get(DetectedSong, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="노래를 찾을 수 없습니다")

    await db.delete(song)
    await db.commit()

    return {"message": "노래가 삭제되었습니다"}


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "music-detect"}
