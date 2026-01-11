# Windows 설치 가이드

Windows 환경에서 Music Detect 앱을 설치하고 실행하는 방법입니다.

## 필수 프로그램 설치

### 1. Python 설치

**권장 버전: Python 3.11 또는 3.12**

현재 Python 3.13을 사용 중이시면, 일부 패키지 호환성 문제가 있을 수 있습니다.

1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.12 다운로드
2. 설치 시 **"Add Python to PATH"** 체크 필수
3. 설치 확인:

```powershell
python --version
```

### 2. Node.js 설치

모바일 앱 개발을 위해 필요합니다.

1. [Node.js 공식 사이트](https://nodejs.org/)에서 LTS 버전 다운로드
2. 설치 진행 (기본 옵션으로 설치)
3. 설치 확인:

```powershell
node --version
npm --version
```

### 3. FFmpeg 설치

오디오 추출을 위해 필수입니다.

**방법 1: Chocolatey 사용 (권장)**

1. PowerShell을 **관리자 권한**으로 실행
2. Chocolatey 설치:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

3. FFmpeg 설치:

```powershell
choco install ffmpeg
```

**방법 2: 수동 설치**

1. [FFmpeg 다운로드](https://www.gyan.dev/ffmpeg/builds/)에서 `ffmpeg-release-essentials.zip` 다운로드
2. 압축 해제 (예: `C:\ffmpeg`)
3. 환경 변수 PATH에 `C:\ffmpeg\bin` 추가:
   - 시스템 속성 → 고급 → 환경 변수
   - 시스템 변수의 Path 편집
   - 새로 만들기 → `C:\ffmpeg\bin` 입력
   - 확인

4. 설치 확인 (새 PowerShell 열기):

```powershell
ffmpeg -version
```

## 백엔드 설치

### 1. 가상 환경 생성

PowerShell 또는 명령 프롬프트에서:

```powershell
cd C:\Users\dsng3\Documents\GitHub\music-detect\backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\activate
```

가상 환경이 활성화되면 프롬프트에 `(venv)`가 표시됩니다:

```
(venv) C:\Users\dsng3\Documents\GitHub\music-detect\backend>
```

### 2. pip 업그레이드

```powershell
python -m pip install --upgrade pip
```

### 3. 의존성 설치

```powershell
pip install -r requirements.txt
```

**설치 중 오류가 발생하면:**

#### pyacoustid 오류

pyacoustid는 `audioread` 의존성이 필요합니다:

```powershell
pip install audioread
pip install chromaprint
```

Chromaprint 바이너리도 필요합니다:

1. [Chromaprint 다운로드](https://acoustid.org/chromaprint)
2. 압축 해제 후 `fpcalc.exe`를 PATH에 추가

또는 간단하게:

```powershell
choco install chromaprint
```

### 4. 환경 변수 설정 (선택사항)

```powershell
copy .env.example .env
```

메모장으로 `.env` 파일 열기:

```powershell
notepad .env
```

필요한 API 키 입력 (ShazamIO와 AcoustID만으로도 충분히 작동합니다):

```env
# 선택사항 - 더 높은 정확도를 원하면 설정
ACRCLOUD_ACCESS_KEY=your_key_here
ACRCLOUD_ACCESS_SECRET=your_secret_here
AUDD_API_TOKEN=your_token_here
```

### 5. 서버 실행

```powershell
# 가상 환경이 활성화된 상태에서
python main.py
```

또는:

```powershell
uvicorn main:app --reload
```

서버가 `http://localhost:8000`에서 실행됩니다.

API 문서 확인: http://localhost:8000/docs

## 모바일 앱 설치 (선택사항)

Windows에서는 Android 앱만 개발할 수 있습니다. (iOS는 macOS 필요)

### 1. Android Studio 설치

1. [Android Studio 다운로드](https://developer.android.com/studio)
2. 설치 시 Android SDK, Android SDK Platform, Android Virtual Device 포함
3. 환경 변수 설정:

```
ANDROID_HOME = C:\Users\dsng3\AppData\Local\Android\Sdk
```

Path에 추가:
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
```

### 2. 모바일 앱 의존성 설치

```powershell
cd C:\Users\dsng3\Documents\GitHub\music-detect\mobile
npm install
```

### 3. Android 에뮬레이터 또는 실제 기기 준비

**에뮬레이터:**
1. Android Studio 실행
2. AVD Manager에서 가상 기기 생성

**실제 기기:**
1. USB 디버깅 활성화
2. USB로 컴퓨터 연결

### 4. 앱 실행

```powershell
npm run android
```

## 문제 해결

### Python 3.13 사용 시 pydantic-core 오류

**해결책 1: Python 3.12 사용 (권장)**

Python 3.12를 설치하고 해당 버전으로 가상 환경을 생성:

```powershell
# Python 3.12 경로 확인
py -3.12 --version

# Python 3.12로 가상 환경 생성
py -3.12 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**해결책 2: 미리 빌드된 wheel 설치**

```powershell
pip install --upgrade pip
pip install pydantic --no-build-isolation
```

**해결책 3: Rust 설치 (권장하지 않음)**

1. [Rust 공식 사이트](https://www.rust-lang.org/tools/install)에서 rustup 다운로드
2. Visual Studio Build Tools 설치 필요

### npm 명령을 찾을 수 없음

Node.js가 제대로 설치되지 않았거나 PATH에 없습니다:

1. Node.js 재설치
2. PowerShell을 **새로 열기** (환경 변수 적용을 위해)
3. 확인:

```powershell
node --version
npm --version
```

### uvicorn 명령을 찾을 수 없음

가상 환경이 활성화되지 않았거나 설치가 실패했습니다:

```powershell
# 가상 환경 활성화 확인
.\venv\Scripts\activate

# uvicorn 재설치
pip install uvicorn[standard]

# 또는 python으로 직접 실행
python main.py
```

### FFmpeg 오류

FFmpeg가 설치되지 않았거나 PATH에 없습니다:

```powershell
# 확인
ffmpeg -version

# 없으면 재설치
choco install ffmpeg
```

PowerShell을 새로 열어 환경 변수를 다시 로드하세요.

### pyacoustid/chromaprint 오류

```powershell
# Chocolatey로 설치
choco install chromaprint

# 또는 수동 다운로드
# https://acoustid.org/chromaprint 에서 다운로드
```

### 포트 이미 사용 중 오류

8000 포트가 이미 사용 중입니다:

```powershell
# 다른 포트 사용
uvicorn main:app --port 8001

# 또는 .env 파일 수정
PORT=8001
```

### 백엔드 서버 접속 오류 (모바일 앱)

Android 에뮬레이터는 `localhost` 대신 `10.0.2.2`를 사용해야 합니다:

`mobile/src/services/api.ts` 수정:

```typescript
// Android 에뮬레이터용
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';
```

실제 기기는 컴퓨터의 IP 주소 사용:

```powershell
# IP 주소 확인
ipconfig
# WiFi 어댑터의 IPv4 주소 확인
```

```typescript
// 실제 기기용
const API_BASE_URL = 'http://192.168.x.x:8000/api/v1';
```

## 빠른 시작 (요약)

```powershell
# 1. 백엔드
cd C:\Users\dsng3\Documents\GitHub\music-detect\backend
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py

# 2. 새 PowerShell에서 모바일 앱 (선택)
cd C:\Users\dsng3\Documents\GitHub\music-detect\mobile
npm install
npm run android
```

## API만 사용하기

모바일 앱 없이 백엔드만 사용할 수도 있습니다:

### cURL로 테스트

```powershell
# 비디오 제출
curl -X POST http://localhost:8000/api/v1/submit -H "Content-Type: application/json" -d "{\"url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\", \"platform\": \"youtube\"}"

# 작업 상태 확인 (job_id는 위 응답에서 받은 값)
curl http://localhost:8000/api/v1/job/1

# 모든 노래 조회
curl http://localhost:8000/api/v1/songs
```

### 브라우저에서 테스트

Swagger UI 사용: http://localhost:8000/docs

## 다음 단계

1. 백엔드 서버가 실행되면 http://localhost:8000/docs에서 API 테스트
2. 실제 인스타그램/틱톡 URL로 음악 감지 테스트
3. 모바일 앱 개발 (선택사항)

질문이 있으면 언제든 물어보세요!
