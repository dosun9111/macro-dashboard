# 📊 거시경제 신호등 대시보드
**Macro Indicator Signal Monitor** — 빅테크 / 테슬라 포트폴리오 최적화용 실시간 거시경제 대시보드

---

## 🎯 개요

지정학적 리스크 (이란-이스라엘 등) 발생 시, 펀드 매니저·기관 투자자들이 모니터링하는  
**핵심 거시경제 지표 5가지**를 실시간으로 시각화하고, 자동으로 신호등(🔴🟡🟢)을 판정해 줍니다.

---

## 📡 모니터링 지표

| 지표 | 심볼 | 위험 기준 | 기회 기준 |
|------|------|-----------|-----------|
| WTI 원유 선물 | `CL=F` | $85~90 돌파 | $80 이하 안정 |
| 미 10년물 국채 금리 | `^TNX` | 4.4% 이상 | 4.1% 이하 하락 |
| VIX 공포 지수 | `^VIX` | 20 이상 상승 | 30 이상 (역발상 매수) |
| 달러 인덱스 (DXY) | `DX-Y.NYB` | 105 이상 | 103 이하 |
| CNN 공포·탐욕 지수 | Alternative.me API | 75 이상 (탐욕) | 25 이하 (극단 공포) |

---

## 🚀 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/macro-dashboard.git
cd macro-dashboard
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## ☁️ Streamlit Cloud 배포 (무료)

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 연동 → 이 레포지토리 선택
3. Main file path: `app.py`
4. **Deploy** 클릭 → 공유 가능한 URL 자동 생성

---

## 📁 폴더 구조

```
macro-dashboard/
│
├── app.py               # 메인 Streamlit 대시보드 앱
├── requirements.txt     # Python 패키지 의존성
├── .gitignore           # Git 제외 파일 목록
└── README.md            # 이 파일
```

---

## ⚠️ 면책 사항

본 대시보드는 **개인 투자 참고용**으로만 사용하세요.  
금융 투자 조언이 아니며, 투자 결정에 대한 책임은 본인에게 있습니다.

---

## 🔧 데이터 소스

- **Yahoo Finance** via `yfinance` 라이브러리 (5분 캐시)
- **CNN Fear & Greed Index** via [Alternative.me API](https://api.alternative.me/fng/) (10분 캐시)
