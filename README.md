# Music Detect - 숏츠 음악 감지 앱

인스타그램 릴스나 틱톡 숏츠에서 마음에 드는 노래를 쉽게 저장하고 찾을 수 있는 앱입니다.

## 주요 기능

- 📱 **공유하기 지원**: 인스타그램/틱톡에서 직접 공유하여 앱으로 전송
- 🎵 **다중 음악 감지**: 한 영상에 여러 곡이 있어도 모두 식별
- 🎯 **높은 정확도**: 여러 무료 음악 감지 서비스를 조합하여 정확성 극대화
- 💾 **자동 저장**: 감지된 노래 자동 저장 및 관리
- 🆓 **완전 무료**: 무료 API만 사용하여 비용 제로

## 기술 스택

### 백엔드
- **Python 3.11+** with FastAPI
- **FFmpeg**: 비디오에서 오디오 추출
- **음악 감지 라이브러리**:
  - ShazamIO (Shazam 비공식)
  - pyacoustid (AcoustID)
  - ACRCloud SDK
  - Audd.io API

### 모바일 앱
- **React Native**: 크로스 플랫폼 개발
- **Share Extension**: iOS/Android 공유하기 기능

### 데이터베이스
- **SQLite**: 감지된 노래 저장

## 프로젝트 구조

```
music-detect/
├── backend/              # Python 백엔드 서버
│   ├── app/
│   │   ├── api/         # API 엔드포인트
│   │   ├── services/    # 음악 감지 서비스
│   │   ├── models/      # 데이터 모델
│   │   └── utils/       # 유틸리티 함수
│   ├── requirements.txt
│   └── main.py
├── mobile/              # React Native 앱
│   ├── src/
│   │   ├── screens/    # 화면 컴포넌트
│   │   ├── components/ # 재사용 컴포넌트
│   │   └── services/   # API 클라이언트
│   └── package.json
└── docs/                # 문서

```

## 시작하기

### 📋 설치 가이드

- **Windows 사용자**: [Windows 설치 가이드](docs/WINDOWS_SETUP.md) 참고
- **macOS/Linux 사용자**: [상세 설치 가이드](docs/SETUP.md) 참고

### 빠른 시작

#### 백엔드 설치 및 실행

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 서버 실행
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

**API 문서**: http://localhost:8000/docs

#### 모바일 앱 설치 (선택사항)

```bash
cd mobile
npm install

# iOS (macOS만 해당)
cd ios && pod install && cd ..
npx react-native run-ios

# Android
npx react-native run-android
```

## 음악 감지 작동 원리

1. **비디오 수신**: 공유하기로 전달된 비디오 URL 수신
2. **오디오 추출**: FFmpeg로 비디오에서 오디오 추출
3. **세그먼트 분할**: 오디오를 여러 세그먼트로 분할 (다중 노래 감지)
4. **병렬 감지**: 여러 무료 서비스에 동시 요청
   - ShazamIO (제한 없음)
   - AcoustID (무제한)
   - ACRCloud (무료: 100회/일)
   - Audd.io (무료: 1,000회/월)
5. **결과 통합**: 여러 서비스 결과를 비교하여 가장 정확한 답 선택
6. **저장**: 감지된 모든 노래를 데이터베이스에 저장

## 무료 API 할당량

- **ShazamIO**: 무제한 (비공식)
- **AcoustID**: 무제한
- **ACRCloud**: 100 requests/day (무료 플랜)
- **Audd.io**: 1,000 requests/month (무료 플랜)

## 라이선스

MIT License

## 기여

이슈와 PR은 언제나 환영합니다!
