# API 문서

## Base URL

```
http://localhost:8000/api/v1
```

## 엔드포인트

### 1. 비디오 제출

비디오 URL을 제출하여 음악 감지를 시작합니다.

**요청:**
```http
POST /submit
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/...",
  "platform": "instagram",
  "services": ["shazam", "acoustid", "audd"]  // 선택사항
}
```

**파라미터:**
- `url` (필수): 비디오 URL
- `platform` (선택): 플랫폼 이름 (instagram, tiktok, youtube 등)
- `services` (선택): 사용할 감지 서비스 배열. 미지정시 모든 서비스 사용

**응답:**
```json
{
  "job_id": 123,
  "status": "pending",
  "message": "비디오 처리가 시작되었습니다"
}
```

**상태 코드:**
- `200`: 성공
- `500`: 서버 오류

### 2. 작업 상태 조회

제출된 작업의 처리 상태를 조회합니다.

**요청:**
```http
GET /job/{job_id}
```

**응답:**
```json
{
  "job_id": 123,
  "status": "completed",
  "progress": 100,
  "songs_detected": 2,
  "error_message": null,
  "songs": [
    {
      "id": 1,
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "release_date": "2023-01-01",
      "service": "shazam",
      "confidence": 0.95,
      "spotify_id": "3n3Ppam7vgaVa1iaRUc9Lp",
      "apple_music_id": "1234567890",
      "isrc": "USUM71234567",
      "detected_at": "2024-01-15T10:30:00"
    }
  ]
}
```

**작업 상태:**
- `pending`: 대기 중
- `processing`: 처리 중
- `completed`: 완료
- `failed`: 실패

**상태 코드:**
- `200`: 성공
- `404`: 작업을 찾을 수 없음

### 3. 모든 노래 조회

저장된 모든 노래 목록을 조회합니다.

**요청:**
```http
GET /songs?limit=50&offset=0
```

**파라미터:**
- `limit` (선택, 기본값: 50): 한 번에 가져올 노래 수
- `offset` (선택, 기본값: 0): 시작 위치

**응답:**
```json
[
  {
    "id": 1,
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "release_date": "2023-01-01",
    "service": "shazam",
    "confidence": 0.95,
    "spotify_id": "3n3Ppam7vgaVa1iaRUc9Lp",
    "apple_music_id": "1234567890",
    "isrc": "USUM71234567",
    "detected_at": "2024-01-15T10:30:00"
  }
]
```

### 4. 노래 삭제

특정 노래를 삭제합니다.

**요청:**
```http
DELETE /song/{song_id}
```

**응답:**
```json
{
  "message": "노래가 삭제되었습니다"
}
```

**상태 코드:**
- `200`: 성공
- `404`: 노래를 찾을 수 없음

### 5. 헬스 체크

서버 상태를 확인합니다.

**요청:**
```http
GET /health
```

**응답:**
```json
{
  "status": "healthy",
  "service": "music-detect"
}
```

## 사용 예제

### cURL

```bash
# 1. 비디오 제출
curl -X POST http://localhost:8000/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/reel/example",
    "platform": "instagram"
  }'

# 2. 작업 상태 확인
curl http://localhost:8000/api/v1/job/123

# 3. 모든 노래 조회
curl http://localhost:8000/api/v1/songs?limit=10

# 4. 노래 삭제
curl -X DELETE http://localhost:8000/api/v1/song/1
```

### JavaScript (Fetch)

```javascript
// 비디오 제출
async function submitVideo(url, platform) {
  const response = await fetch('http://localhost:8000/api/v1/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, platform }),
  });

  return await response.json();
}

// 작업 상태 확인
async function getJobStatus(jobId) {
  const response = await fetch(`http://localhost:8000/api/v1/job/${jobId}`);
  return await response.json();
}

// 노래 목록 조회
async function getSongs(limit = 50, offset = 0) {
  const response = await fetch(
    `http://localhost:8000/api/v1/songs?limit=${limit}&offset=${offset}`
  );
  return await response.json();
}
```

### Python (requests)

```python
import requests

# 비디오 제출
def submit_video(url, platform="unknown"):
    response = requests.post(
        "http://localhost:8000/api/v1/submit",
        json={"url": url, "platform": platform}
    )
    return response.json()

# 작업 상태 확인
def get_job_status(job_id):
    response = requests.get(f"http://localhost:8000/api/v1/job/{job_id}")
    return response.json()

# 노래 목록 조회
def get_songs(limit=50, offset=0):
    response = requests.get(
        "http://localhost:8000/api/v1/songs",
        params={"limit": limit, "offset": offset}
    )
    return response.json()
```

## 오류 처리

모든 API는 오류 발생 시 다음과 같은 형식으로 응답합니다:

```json
{
  "detail": "오류 메시지"
}
```

**일반적인 오류 코드:**
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 속도 제한

현재 속도 제한은 없지만, 무료 API 서비스의 제한이 있습니다:

- **ShazamIO**: 제한 없음 (비공식)
- **AcoustID**: 제한 없음
- **ACRCloud**: 100 requests/day (무료 플랜)
- **Audd.io**: 1,000 requests/month (무료 플랜)

## WebSocket (향후 계획)

실시간 진행 상황 업데이트를 위한 WebSocket 지원 예정:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/job/123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```

## Interactive API 문서

FastAPI의 자동 생성 문서를 통해 API를 테스트할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
