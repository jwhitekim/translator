# Translation Studio

DeepL + Free Dictionary API 통합 번역 도구. 단일 HTML 파일.

## 실행 방법

### 방법 1: 파일 더블클릭 (CORS 오류 없으면 OK)
`index.html` 파일을 브라우저로 열기.

### 방법 2: 로컬 서버 (권장 — CORS 오류 발생 시)
```bash
cd translator/
python -m http.server 8080
# 브라우저에서 http://localhost:8080 접속
```

## DeepL API Key 발급

1. https://www.deepl.com/pro-api 접속
2. 계정 생성 → **Free Plan** 선택
3. API Key 복사
4. `index.html` 실행 후 우측 상단 입력창에 붙여넣기
   - 입력한 키는 브라우저 `localStorage`에 자동 저장됨

> Free tier: 월 500,000자 무료. 개인 논문 읽기 용도로 충분.  
> **주의:** Free tier는 `api-free.deepl.com` 엔드포인트 사용. Pro는 `api.deepl.com`. 혼용 시 403 오류.

## 사용법

1. 왼쪽 영역에 영어 텍스트 붙여넣기
2. **번역하기** 버튼 클릭 또는 `Ctrl+Enter`
3. 오른쪽 번역 결과에서 모르는 단어 클릭 → 하단 사전 패널에 뜻 표시
4. 한국어 뜻이 필요하면 **네이버 사전에서 보기 →** 클릭
