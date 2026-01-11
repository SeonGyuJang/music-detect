# 아키텍처 문서

## 시스템 개요

Music Detect는 소셜 미디어 영상에서 음악을 자동으로 감지하고 저장하는 시스템입니다.

```
┌─────────────┐
│   Mobile    │
│     App     │ (React Native)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│   Backend   │
│   FastAPI   │ (Python)
└──────┬──────┘
       │
       ├──────► 비디오 다운로드 (yt-dlp)
       │
       ├──────► 오디오 추출 (FFmpeg/pydub)
       │
       ├──────► 음악 감지 서비스들
       │        ├─ ShazamIO
       │        ├─ AcoustID
       │        ├─ ACRCloud
       │        └─ Audd.io
       │
       └──────► 데이터베이스 (SQLite)
```

## 주요 컴포넌트

### 1. 모바일 앱 (React Native)

**역할:**
- 사용자 인터페이스 제공
- 공유 인텐트 수신
- 백엔드 API 호출
- 감지된 노래 목록 표시

**주요 화면:**
- `HomeScreen`: 저장된 노래 목록
- `ProcessingScreen`: 처리 진행 상황
- `App`: 공유 인텐트 처리 및 라우팅

**기술 스택:**
- React Native 0.73
- React Navigation
- Axios (HTTP 클라이언트)
- React Native Share Menu (공유 기능)

### 2. 백엔드 서버 (FastAPI)

**역할:**
- RESTful API 제공
- 비디오 다운로드 및 오디오 추출
- 음악 감지 서비스 조율
- 데이터 저장 및 관리

**계층 구조:**

```
backend/
├── main.py                    # FastAPI 앱 진입점
├── app/
│   ├── api/
│   │   └── routes.py         # API 엔드포인트
│   ├── services/
│   │   └── music_recognition.py  # 음악 감지 통합
│   ├── models/
│   │   └── database.py       # 데이터베이스 모델
│   └── utils/
│       └── audio_extractor.py    # 오디오 추출 유틸리티
```

**기술 스택:**
- FastAPI (웹 프레임워크)
- SQLAlchemy (ORM)
- aiosqlite (비동기 SQLite)
- yt-dlp (비디오 다운로드)
- pydub (오디오 처리)
- shazamio, pyacoustid (음악 감지)

### 3. 음악 감지 시스템

여러 무료 서비스를 병렬로 사용하여 정확도를 극대화합니다.

#### 3.1 ShazamRecognizer

**특징:**
- Shazam 비공식 라이브러리 (shazamio)
- 제한 없음
- 높은 정확도
- Spotify/Apple Music ID 제공

**장점:**
- 완전 무료
- 빠른 응답 속도
- 최신 곡 데이터베이스

**단점:**
- 비공식 API (변경 가능성)

#### 3.2 AcoustIDRecognizer

**특징:**
- 오픈소스 음악 지문 인식
- MusicBrainz 데이터베이스 사용
- 완전 무료, 무제한

**장점:**
- 공식 API
- 신뢰성 높음
- 상세한 메타데이터

**단점:**
- 최신 곡 데이터베이스가 부족할 수 있음
- Spotify/Apple Music ID 미제공

#### 3.3 ACRCloud (선택사항)

**특징:**
- 상용 서비스의 무료 플랜
- 100 requests/day

**장점:**
- 높은 정확도
- 빠른 응답

**단점:**
- 일일 제한
- API 키 필요

#### 3.4 Audd.io (선택사항)

**특징:**
- 무료 플랜 1,000 requests/month

**장점:**
- Spotify/Apple Music 통합
- 가사 정보 제공 (유료)

**단점:**
- 월별 제한
- API 키 필요

### 4. 음악 감지 전략

#### 병렬 처리

```python
async def recognize_single(audio_path):
    tasks = [
        shazam.recognize(audio_path),
        acoustid.recognize(audio_path),
        audd.recognize(audio_path)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### 결과 통합

1. **신뢰도 기반 선택**: 가장 높은 신뢰도 점수의 결과 선택
2. **정보 보완**: 다른 서비스의 결과로 누락된 정보 채움
3. **중복 제거**: 같은 곡의 중복 제거

```python
def merge_results(songs: List[SongMatch]) -> SongMatch:
    # 신뢰도순 정렬
    songs.sort(key=lambda s: s.confidence, reverse=True)
    best = songs[0]

    # 정보 보완
    for song in songs[1:]:
        if not best.spotify_id and song.spotify_id:
            best.spotify_id = song.spotify_id
        # ...

    return best
```

### 5. 다중 노래 감지

한 영상에 여러 노래가 있을 수 있으므로 오디오를 세그먼트로 분할합니다.

```
전체 오디오 (60초)
├── 세그먼트 0: 0-10초
├── 세그먼트 1: 8-18초  (2초 겹침)
├── 세그먼트 2: 16-26초
├── 세그먼트 3: 24-34초
├── 세그먼트 4: 32-42초
└── 세그먼트 5: 40-50초
```

**파라미터:**
- `segment_duration`: 10초
- `overlap`: 2초

**중복 제거:**
같은 노래가 여러 세그먼트에서 감지될 수 있으므로 제목+아티스트로 중복 제거합니다.

## 데이터 모델

### DetectedSong

```python
class DetectedSong:
    id: int
    title: str
    artist: str
    album: Optional[str]
    release_date: Optional[str]
    detection_service: str
    confidence: float
    video_url: str
    video_platform: str
    isrc: Optional[str]
    spotify_id: Optional[str]
    apple_music_id: Optional[str]
    genre: Optional[str]
    duration_ms: Optional[int]
    detected_at: datetime
    timestamp_in_video: Optional[float]
    raw_response: Optional[str]
```

### VideoProcessingJob

```python
class VideoProcessingJob:
    id: int
    video_url: str
    platform: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    songs_detected: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

## 처리 흐름

### 1. 비디오 제출

```
사용자 → 공유하기 → 앱
  ↓
앱 → POST /submit → 백엔드
  ↓
작업 생성 (JobID 반환)
  ↓
백그라운드 태스크 시작
```

### 2. 백그라운드 처리

```
1. 비디오 다운로드 (yt-dlp)
   ├─ 인스타그램
   ├─ 틱톡
   └─ 유튜브 등

2. 오디오 추출 (FFmpeg/pydub)
   └─ MP3 변환

3. 세그먼트 분할
   └─ 10초씩, 2초 겹침

4. 병렬 음악 감지
   ├─ ShazamIO
   ├─ AcoustID
   ├─ ACRCloud (선택)
   └─ Audd.io (선택)

5. 결과 통합
   ├─ 신뢰도 기반 선택
   ├─ 정보 보완
   └─ 중복 제거

6. 데이터베이스 저장

7. 임시 파일 정리
```

### 3. 진행 상황 모니터링

```
앱 → GET /job/{id} (폴링)
  ↓
백엔드 → 작업 상태 반환
  ↓
앱 → UI 업데이트
```

## 확장성 고려사항

### 현재 한계

- SQLite 사용 (단일 서버)
- 백그라운드 태스크 (프로세스 재시작 시 손실)
- 폴링 방식 (실시간성 부족)

### 확장 방안

1. **데이터베이스**
   - SQLite → PostgreSQL
   - 다중 서버 지원

2. **작업 큐**
   - BackgroundTasks → Celery + Redis
   - 작업 지속성 및 재시도

3. **실시간 업데이트**
   - 폴링 → WebSocket
   - Server-Sent Events

4. **캐싱**
   - Redis 캐시
   - 중복 비디오 처리 방지

5. **CDN**
   - 비디오 저장 → S3
   - 트래픽 분산

## 보안 고려사항

### 현재 구현

- CORS 허용 (개발 환경)
- HTTP (프로덕션에서는 HTTPS 필요)

### 프로덕션 권장사항

1. **HTTPS 사용**
2. **API 키 인증**
3. **Rate Limiting**
4. **입력 검증**
5. **CORS 제한**

## 성능 최적화

### 병렬 처리

- 여러 감지 서비스 동시 호출
- asyncio 사용

### 캐싱 전략

- 같은 비디오 URL 중복 처리 방지
- 감지 결과 캐싱

### 리소스 관리

- 임시 파일 자동 정리
- 메모리 효율적인 스트리밍

## 모니터링 및 로깅

### 로그 레벨

- INFO: 일반 작업 진행
- WARNING: 경고 (API 실패 등)
- ERROR: 오류

### 주요 메트릭

- 작업 처리 시간
- 감지 성공률
- API 응답 시간
- 오류율

## 테스트 전략

### 단위 테스트

- 각 음악 감지 서비스
- 오디오 추출 유틸리티
- API 엔드포인트

### 통합 테스트

- 전체 비디오 처리 흐름
- 데이터베이스 연동

### E2E 테스트

- 모바일 앱에서 서버까지
- 실제 비디오 URL 사용
