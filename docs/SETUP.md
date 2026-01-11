# 설치 및 설정 가이드

## 필수 요구사항

### 시스템 요구사항
- Python 3.11 이상
- Node.js 18 이상
- FFmpeg (오디오 처리용)
- React Native 개발 환경 (iOS: Xcode, Android: Android Studio)

### FFmpeg 설치

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
- [FFmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 다운로드
- PATH 환경 변수에 추가

## 백엔드 설정

### 1. Python 가상 환경 생성

```bash
cd backend
python -m venv venv

# 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 수정:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
# ACRCloud 설정 (선택사항 - 무료 플랜 가입 필요)
# https://www.acrcloud.com/ 에서 가입 후 키 발급
ACRCLOUD_ACCESS_KEY=your_key_here
ACRCLOUD_ACCESS_SECRET=your_secret_here
ACRCLOUD_HOST=identify-eu-west-1.acrcloud.com

# Audd.io 설정 (선택사항 - 무료 플랜 가입 필요)
# https://audd.io/ 에서 가입 후 토큰 발급
AUDD_API_TOKEN=your_token_here

# 서버 설정
PORT=8000
HOST=0.0.0.0
DEBUG=True

# 데이터베이스
DATABASE_URL=sqlite+aiosqlite:///./music_detect.db

# 임시 파일 경로
TEMP_DIR=./temp
```

**참고:** ACRCloud와 Audd.io는 선택사항입니다.
설정하지 않아도 ShazamIO와 AcoustID가 작동합니다.

### 4. 서버 실행

```bash
cd backend
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

API 문서: `http://localhost:8000/docs`

## 모바일 앱 설정

### 1. 의존성 설치

```bash
cd mobile
npm install
```

### 2. iOS 설정 (macOS만 해당)

```bash
cd ios
pod install
cd ..
```

**공유하기 Extension 설정:**

iOS에서 공유하기 기능을 사용하려면 Share Extension을 설정해야 합니다.

1. Xcode에서 `mobile/ios/MusicDetectApp.xcworkspace` 열기
2. File > New > Target > Share Extension 추가
3. `Info.plist`에 다음 추가:

```xml
<key>NSExtensionActivationRule</key>
<dict>
    <key>NSExtensionActivationSupportsWebURLWithMaxCount</key>
    <integer>1</integer>
</dict>
```

### 3. Android 설정

**AndroidManifest.xml 수정:**

`mobile/android/app/src/main/AndroidManifest.xml`에 다음 추가:

```xml
<activity
    android:name=".ShareActivity"
    android:label="@string/app_name">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

### 4. API URL 설정

`mobile/src/services/api.ts` 파일에서 API URL 수정:

```typescript
// 개발 환경
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 프로덕션 환경
// const API_BASE_URL = 'https://your-api-domain.com/api/v1';
```

**Android 에뮬레이터 사용 시:**
```typescript
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';
```

**실제 기기 사용 시:**
```typescript
const API_BASE_URL = 'http://YOUR_COMPUTER_IP:8000/api/v1';
```

### 5. 앱 실행

**iOS:**
```bash
npm run ios
```

**Android:**
```bash
npm run android
```

## 테스트

### 백엔드 테스트

```bash
cd backend

# 헬스 체크
curl http://localhost:8000/api/v1/health

# 비디오 제출 테스트
curl -X POST http://localhost:8000/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "platform": "youtube"
  }'
```

### 모바일 앱 테스트

1. 백엔드 서버가 실행 중인지 확인
2. 모바일 앱 실행
3. 인스타그램/틱톡 앱에서 영상 공유하기
4. "Music Detect" 앱 선택
5. 자동으로 음악 감지 시작

## 문제 해결

### FFmpeg 오류
```
RuntimeError: ffprobe was not found
```

**해결:** FFmpeg가 설치되었는지 확인하고 PATH에 추가되었는지 확인

```bash
ffmpeg -version
```

### Python 의존성 오류
```
ModuleNotFoundError: No module named 'shazamio'
```

**해결:** 가상 환경 활성화 후 의존성 재설치

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 네트워크 오류 (모바일 앱)
```
Network Error: connect ECONNREFUSED
```

**해결:**
1. 백엔드 서버가 실행 중인지 확인
2. API URL이 올바른지 확인 (특히 Android 에뮬레이터의 경우 10.0.2.2 사용)
3. 방화벽 설정 확인

### 음악 감지 실패

**원인:**
- 오디오 품질이 낮음
- 노이즈가 많음
- 음악이 너무 짧음 (10초 미만)
- 데이터베이스에 없는 곡

**해결:**
- 여러 감지 서비스를 활성화
- 비디오 품질 향상
- 더 긴 구간의 비디오 사용

## 무료 API 키 발급

### ACRCloud (선택사항)

1. https://www.acrcloud.com/ 방문
2. 회원가입
3. Console > Audio & Video Recognition 프로젝트 생성
4. Access Key, Access Secret, Host 복사
5. `.env` 파일에 추가

**무료 플랜:** 100 requests/day

### Audd.io (선택사항)

1. https://audd.io/ 방문
2. 회원가입
3. Dashboard에서 API Token 확인
4. `.env` 파일에 추가

**무료 플랜:** 1,000 requests/month

**참고:** 무료 서비스(ShazamIO, AcoustID)만으로도 충분히 작동합니다!
