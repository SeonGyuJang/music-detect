"""FastAPI 메인 애플리케이션"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from app.api import router
from app.models import init_db

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 이벤트"""
    # 시작 시
    logger.info("애플리케이션 시작")

    # 데이터베이스 초기화
    await init_db()
    logger.info("데이터베이스 초기화 완료")

    # temp 디렉토리 생성
    temp_dir = os.getenv("TEMP_DIR", "./temp")
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"임시 디렉토리 생성: {temp_dir}")

    yield

    # 종료 시
    logger.info("애플리케이션 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="Music Detect API",
    description="숏츠 영상에서 음악을 감지하는 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix="/api/v1", tags=["music-detection"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Music Detect API",
        "version": "1.0.0",
        "description": "숏츠 영상에서 음악을 자동으로 감지합니다",
        "endpoints": {
            "submit": "POST /api/v1/submit - 비디오 URL 제출",
            "job_status": "GET /api/v1/job/{job_id} - 작업 상태 조회",
            "songs": "GET /api/v1/songs - 모든 노래 조회",
            "health": "GET /api/v1/health - 헬스 체크"
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "True") == "True"
    )
