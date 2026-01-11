# 사용 가이드

## 사용자 가이드

### 앱 설치

1. 백엔드 서버 실행
2. 모바일 앱 빌드 및 설치
3. 앱 실행하여 초기 설정 확인

### 음악 감지하기

#### 방법 1: 인스타그램 릴스

1. 인스타그램 앱 열기
2. 마음에 드는 릴스 찾기
3. 공유하기 버튼 (종이비행기 아이콘) 탭
4. "Music Detect" 앱 선택
5. 자동으로 음악 감지 시작

#### 방법 2: 틱톡

1. 틱톡 앱 열기
2. 마음에 드는 영상 찾기
3. 공유하기 버튼 탭
4. "Music Detect" 앱 선택
5. 자동으로 음악 감지 시작

#### 방법 3: 유튜브 쇼츠

1. 유튜브 앱 열기
2. 쇼츠 영상 찾기
3. 공유하기 버튼 탭
4. "Music Detect" 앱 선택
5. 자동으로 음악 감지 시작

### 감지 과정

1. **비디오 다운로드** (5-10초)
   - 공유된 URL에서 비디오 다운로드

2. **오디오 추출** (3-5초)
   - 비디오에서 오디오만 추출

3. **음악 감지** (10-30초)
   - 여러 서비스를 통해 음악 식별
   - 한 영상에 여러 곡이 있으면 모두 감지

4. **결과 저장**
   - 감지된 노래들을 자동 저장

### 노래 목록 보기

1. 앱의 홈 화면에서 저장된 노래 확인
2. 아래로 당겨서 새로고침
3. 각 노래 카드에는 다음 정보 표시:
   - 제목 및 아티스트
   - 앨범 (있는 경우)
   - 감지 서비스
   - 신뢰도 점수

### 노래 재생하기

각 노래 카드의 오른쪽에 있는 버튼:

- **Spotify 버튼** (초록색): Spotify에서 재생
- **Apple Music 버튼** (빨간색): Apple Music에서 재생
- **삭제 버튼**: 노래 삭제

### 팁

#### 높은 정확도를 위한 팁

1. **긴 영상 선택**: 10초 이상의 영상이 좋습니다
2. **음악이 명확한 영상**: 배경 소음이 적을수록 좋습니다
3. **원본 음원 사용**: 리믹스나 커버보다 원곡이 정확도가 높습니다
4. **전체 감지 서비스 사용**: 설정에서 모든 서비스 활성화

#### 문제 해결

**음악을 찾을 수 없다고 나옵니다**
- 영상이 너무 짧을 수 있습니다 (10초 이상 권장)
- 배경 소음이 너무 많을 수 있습니다
- 데이터베이스에 없는 신곡이거나 비주류 음악일 수 있습니다
- 다른 영상으로 다시 시도해보세요

**처리가 너무 오래 걸립니다**
- 영상 길이에 따라 30초~2분 소요될 수 있습니다
- 네트워크 속도가 느릴 수 있습니다
- 백엔드 서버 상태를 확인하세요

**앱이 공유 목록에 나타나지 않습니다**
- iOS: Share Extension이 올바르게 설정되었는지 확인
- Android: AndroidManifest.xml의 intent-filter 확인
- 앱 재설치 시도

## 개발자 가이드

### 로컬 개발 환경

#### 백엔드 개발

```bash
cd backend

# 가상 환경 활성화
source venv/bin/activate

# 개발 모드로 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**자동 재로딩**: 코드 변경 시 자동으로 서버 재시작

**API 문서**: http://localhost:8000/docs

#### 모바일 앱 개발

```bash
cd mobile

# Metro 서버 시작
npm start

# iOS 실행 (별도 터미널)
npm run ios

# Android 실행 (별도 터미널)
npm run android
```

**Hot Reload**: 코드 변경 시 자동 반영

### 새로운 음악 감지 서비스 추가

1. `backend/app/services/music_recognition.py`에 새 클래스 추가:

```python
class NewServiceRecognizer:
    async def recognize(self, audio_path: str) -> Optional[SongMatch]:
        # 구현
        pass
```

2. `MusicRecognitionService`에 통합:

```python
def __init__(self):
    self.new_service = NewServiceRecognizer()

async def recognize_single(self, audio_path, services=None):
    if 'new_service' in services:
        tasks.append(self.new_service.recognize(audio_path))
```

### 데이터베이스 스키마 변경

1. `backend/app/models/database.py`에서 모델 수정

2. Alembic 마이그레이션 생성:

```bash
cd backend
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

### API 엔드포인트 추가

`backend/app/api/routes.py`에 새 엔드포인트 추가:

```python
@router.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}
```

### 모바일 화면 추가

1. `mobile/src/screens/`에 새 화면 생성
2. `mobile/src/App.tsx`에서 라우팅 추가

### 테스트

#### 백엔드 테스트

```bash
cd backend
pytest
```

#### 모바일 앱 테스트

```bash
cd mobile
npm test
```

### 디버깅

#### 백엔드 디버깅

로그 확인:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("디버그 메시지")
```

#### 모바일 디버깅

React Native Debugger:
```bash
# Chrome 개발자 도구
# iOS: Cmd+D → Debug
# Android: Cmd+M → Debug
```

### 배포

#### 백엔드 배포

1. **Docker 사용** (권장):

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t music-detect-backend .
docker run -p 8000:8000 music-detect-backend
```

2. **일반 서버**:

```bash
# Gunicorn 사용
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 모바일 앱 배포

**iOS:**
```bash
cd mobile/ios
# 프로덕션 빌드
xcodebuild -workspace MusicDetectApp.xcworkspace \
  -scheme MusicDetectApp \
  -configuration Release
```

**Android:**
```bash
cd mobile/android
./gradlew assembleRelease
```

### 환경별 설정

#### 개발 환경

```typescript
// mobile/src/services/api.ts
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

#### 프로덕션 환경

```typescript
const API_BASE_URL = 'https://api.yourdomain.com/api/v1';
```

환경 변수 사용:
```bash
# .env
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
```

### 성능 최적화

1. **백엔드**:
   - Redis 캐싱 추가
   - 데이터베이스 인덱싱
   - 비동기 처리 최적화

2. **모바일**:
   - 이미지 최적화
   - 리스트 가상화
   - 메모리 관리

### 모니터링

#### 백엔드 모니터링

```python
# 로그 파일 설정
logging.basicConfig(
    filename='app.log',
    level=logging.INFO
)
```

#### 앱 크래시 리포팅

- Sentry 통합
- Firebase Crashlytics

### CI/CD

#### GitHub Actions 예제

```yaml
name: CI/CD

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest
```

## 고급 기능

### 커스텀 음악 데이터베이스

자체 음악 데이터베이스 연동 가능:

```python
class CustomRecognizer:
    def __init__(self, db_path):
        self.db = load_database(db_path)

    async def recognize(self, audio_path):
        fingerprint = generate_fingerprint(audio_path)
        matches = self.db.search(fingerprint)
        return matches[0] if matches else None
```

### 배치 처리

여러 비디오 동시 처리:

```bash
curl -X POST http://localhost:8000/api/v1/batch \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [
      {"url": "https://..."},
      {"url": "https://..."}
    ]
  }'
```

### 웹훅

처리 완료 시 웹훅 호출:

```python
@router.post("/submit")
async def submit_video(request: VideoSubmitRequest, webhook_url: str = None):
    # 처리 완료 시
    if webhook_url:
        await notify_webhook(webhook_url, result)
```
