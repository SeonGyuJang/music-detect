from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, Float
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./music_detect.db")

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class DetectedSong(Base):
    """감지된 노래 정보"""
    __tablename__ = "detected_songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 노래 정보
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str] = mapped_column(String(500), nullable=False)
    album: Mapped[str] = mapped_column(String(500), nullable=True)
    release_date: Mapped[str] = mapped_column(String(50), nullable=True)

    # 감지 정보
    detection_service: Mapped[str] = mapped_column(String(50), nullable=False)  # shazam, acoustid, acrcloud, audd
    confidence: Mapped[float] = mapped_column(Float, nullable=True)  # 신뢰도 점수

    # 원본 비디오 정보
    video_url: Mapped[str] = mapped_column(Text, nullable=True)
    video_platform: Mapped[str] = mapped_column(String(50), nullable=True)  # instagram, tiktok

    # 음악 식별자
    isrc: Mapped[str] = mapped_column(String(50), nullable=True)  # International Standard Recording Code
    spotify_id: Mapped[str] = mapped_column(String(100), nullable=True)
    apple_music_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # 메타데이터
    genre: Mapped[str] = mapped_column(String(100), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)

    # 타임스탬프
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    timestamp_in_video: Mapped[float] = mapped_column(Float, nullable=True)  # 비디오 내 위치 (초)

    # 추가 JSON 데이터
    raw_response: Mapped[str] = mapped_column(Text, nullable=True)  # API 원본 응답


class VideoProcessingJob(Base):
    """비디오 처리 작업"""
    __tablename__ = "video_processing_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, processing, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    songs_detected: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


async def init_db():
    """데이터베이스 초기화"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """데이터베이스 세션 가져오기"""
    async with async_session_maker() as session:
        yield session
