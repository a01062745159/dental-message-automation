# 🏥 서울수려한치과 - 자동 문자 발송 시스템

Streamlit 기반의 전문적인 자동 문자 발송 시스템입니다.

## 🎯 기능

- **📱 통화 기록 입력**: 전화 상담원이 통화 내용 입력
- **✉️ 메시지 자동 생성**: 상황별 템플릿으로 자동 생성
- **📊 발송 관리**: 발송 현황 및 기록 관리

## 🚀 빠른 시작

### 1️⃣ 로컬 테스트 (선택사항)

```bash
# 필요한 라이브러리 설치
pip install -r requirements.txt

# Streamlit 실행
streamlit run app.py
```

### 2️⃣ Google Cloud 설정 (필수)

#### Step 1: Google Cloud 프로젝트 생성
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성
3. 프로젝트 ID 복사

#### Step 2: Google Sheets API 활성화
1. "API 및 서비스" → "라이브러리" 클릭
2. "Google Sheets API" 검색 및 활성화
3. "Google Drive API" 검색 및 활성화

#### Step 3: 서비스 계정 생성
1. "API 및 서비스" → "사용자 인증 정보" 클릭
2. "사용자 인증 정보 만들기" → "서비스 계정"
3. 이름 입력 (예: `dental-app`)
4. "만들기" → "계속" → "완료"

#### Step 4: 키 생성
1. 방금 만든 서비스 계정 선택
2. "키" 탭 → "키 추가" → "새 키 만들기"
3. "JSON" 선택 후 다운로드
4. 다운로드된 파일 열어서 내용 복사

### 3️⃣ GitHub 리포지토리 설정

#### Step 1: 파일 업로드
1. GitHub 리포지토리에서 다음 파일 업로드:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`

#### Step 2: secrets 폴더 생성
1. `.streamlit` 폴더 생성
2. 파일 생성: `.streamlit/secrets.toml`
3. 아래 내용 입력:

```toml
spreadsheet_id = "당신의_스프레드시트_ID"

[gsheet_creds]
type = "service_account"
project_id = "..."
private_key_id = "..."
# ... (Step 4에서 복사한 JSON 전체 내용)
```

### 4️⃣ Streamlit Cloud 배포

1. https://streamlit.io/cloud 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. Repository: `a01062745159/dental-message-automation`
5. Branch: `main`
6. Main file path: `app.py`
7. "Deploy" 클릭

#### secrets 설정 (Streamlit Cloud)
1. 앱 설정 → "Secrets" 클릭
2. Step 4의 `secrets.toml` 내용 붙여넣기
3. 저장

### 5️⃣ Google Sheets 권한 설정

1. Google Sheets 열기
2. 공유 아이콘 클릭
3. Step 4에서 복사한 JSON의 `client_email` 복사
4. 해당 이메일에 **편집 권한** 부여

---

## 📊 Google Sheets 구조

### 필요한 시트 (자동 생성됨)
- `기록_전화상담+예약`
- `기록_전화상담+미예약`
- `기록_내원상담+예약`
- `기록_내원상담+미예약`
- `기록_리콜종료`

### 데이터 구조
```
시간 | 상황 | 환자명 | 예약일 | 개인정보 | ...
```

---

## 🎯 사용 방법

### 📱 통화 기록 입력
1. "통화 기록 입력" 탭 선택
2. 상황 선택 (예: 전화상담+예약)
3. 정보 입력
4. "저장" 클릭

### ✉️ 메시지 생성
1. "문자 생성" 탭 선택
2. 미처리 기록 선택
3. "메시지 생성" 클릭
4. 메시지 미리보기 및 복사
5. 카톡/문자로 발송

### 📊 발송 관리
1. "발송 관리" 탭 선택
2. 발송 현황 확인
3. 상세 기록 확인

---

## 🔐 보안

- Google Sheets API를 통한 안전한 연동
- 서비스 계정으로 클라이언트 인증
- Streamlit Cloud의 secrets로 안전하게 관리

---

## 📞 지원

문제가 발생하면:
1. 콘솔 오류 메시지 확인
2. `.streamlit/secrets.toml` 형식 확인
3. Google Cloud 권한 확인

---

## 📝 라이선스

사내용 전용

---

**제작**: Claude | **수정**: 2024.05.15
