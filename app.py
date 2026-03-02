import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="거시경제 신호등 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0c10 !important;
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Sans', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="block-container"] { padding: 1.5rem 2rem !important; }

.signal-card {
    background: #0f1117;
    border: 1px solid #1e2435;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}
.signal-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.signal-card.danger::before  { background: #ef4444; box-shadow: 0 0 12px #ef4444aa; }
.signal-card.warning::before { background: #f59e0b; box-shadow: 0 0 12px #f59e0baa; }
.signal-card.safe::before    { background: #22c55e; box-shadow: 0 0 12px #22c55eaa; }
.signal-card.neutral::before { background: #64748b; }

.signal-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 2px; color: #64748b; margin-bottom: 4px; }
.signal-value { font-family: 'IBM Plex Mono', monospace; font-size: 28px; font-weight: 600; line-height: 1.1; }
.signal-change { font-family: 'IBM Plex Mono', monospace; font-size: 13px; margin-top: 4px; }
.signal-status {
    display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
    margin-top: 8px; font-family: 'IBM Plex Mono', monospace;
}
.status-danger  { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
.status-warning { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
.status-safe    { background: #22c55e22; color: #22c55e; border: 1px solid #22c55e44; }
.status-neutral { background: #64748b22; color: #94a3b8; border: 1px solid #64748b44; }

.overall-banner { border-radius: 10px; padding: 14px 22px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; font-family: 'IBM Plex Mono', monospace; }
.overall-danger  { background: #ef444411; border: 1px solid #ef444433; }
.overall-warning { background: #f59e0b11; border: 1px solid #f59e0b33; }
.overall-safe    { background: #22c55e11; border: 1px solid #22c55e33; }

.section-header { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 3px; color: #475569; border-bottom: 1px solid #1e2435; padding-bottom: 6px; margin: 20px 0 12px 0; }
[data-testid="stDataFrame"] { border: 1px solid #1e2435 !important; border-radius: 8px !important; }
thead th { background: #0f1117 !important; color: #64748b !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# DATA FETCHING (10년치 데이터로 변경)
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_market_data():
    try:
        import yfinance as yf
        tickers = {"WTI": "CL=F", "TNX": "^TNX", "VIX": "^VIX", "DXY": "DX-Y.NYB"}
        results = {}
        
        for name, ticker in tickers.items():
            try:
                t = yf.Ticker(ticker)
                # 10년치 데이터 호출
                hist = t.history(period="10y", interval="1d")
                if not hist.empty and "Close" in hist.columns:
                    hist = hist.dropna(subset=["Close"])

                if len(hist) >= 2:
                    current = hist["Close"].iloc[-1]
                    prev    = hist["Close"].iloc[-2]
                    change  = current - prev
                    pct     = (change / prev) * 100
                    
                    results[name] = {
                        "value": round(current, 2),
                        "change": round(change, 2),
                        "pct": round(pct, 2),
                        "df": hist[["Close"]].copy() # 10년치 차트용 DataFrame 저장
                    }
                else:
                    results[name] = None
            except Exception:
                results[name] = None
        return results, datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
    except ImportError:
        return None, "yfinance not installed"


@st.cache_data(ttl=600)
def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=2", timeout=5)
        data = r.json()["data"]
        current = int(data[0]["value"])
        prev    = int(data[1]["value"]) if len(data) > 1 else current
        return {"value": current, "prev": prev}
    except Exception:
        return None


# ─────────────────────────────────────────
# SIGNAL LOGIC ( UI와 일치하도록 직관성 오류 수정)
# ─────────────────────────────────────────
def get_signal(indicator, value):
    if value is None: return "neutral", "데이터 없음"
    if indicator == "WTI":
        if value >= 90:   return "danger",  "🔴 시장 압박 — 현금 대기"
        elif value >= 85: return "warning", "🟡 인플레 경계 — 관망"
        elif value <= 80: return "safe",    "🟢 물가 안정 — 정상 구간"
        else:             return "neutral", "⚪ 관찰 — 모니터링"
    if indicator == "TNX":
        if value >= 4.4:   return "danger",  "🔴 기술주 타격 — 예수금 방어"
        elif value >= 4.3: return "warning", "🟡 금리 부담 — 주의 구간"
        elif value <= 4.1: return "safe",    "🟢 우호적 환경 — 비중 확대"
        else:              return "neutral", "⚪ 중립 — 관찰 구간"
    if indicator == "VIX":
        if value >= 30:   return "danger",  "🔴 극단 공포 — 분할 매수 개시!"
        elif value >= 20: return "warning", "🟡 변동성 확대 — 경계"
        elif value < 15:  return "safe",    "🟢 안정 — 평온 구간"
        else:             return "neutral", "⚪ 관찰 — 정상 범위"
    if indicator == "DXY":
        if value >= 105:   return "danger",  "🔴 강달러 — 빅테크 실적 압박"
        elif value >= 103: return "warning", "🟡 달러 강세 — 주의"
        else:              return "safe",    "🟢 약달러 — 기술주 우호적"
    if indicator == "FNG":
        if value <= 25:   return "danger",  "🔴 극단 공포 — 현금 투입!"
        elif value <= 40: return "warning", "🟡 공포 — 투심 위축"
        elif value >= 75: return "warning", "🟡 극단 탐욕 — 신규 매수 자제"
        else:             return "safe",    "🟢 정상 — 펀더멘털 집중"
    return "neutral", "—"

def overall_signal(signals):
    counts = {"danger": 0, "warning": 0, "safe": 0, "neutral": 0}
    for s in signals: counts[s] = counts.get(s, 0) + 1
    if counts["danger"] >= 2: return "danger",  "위험 구간 — 현금 비중 확대 권고"
    elif counts["safe"] >= 3: return "safe",    "기회 구간 — 분할 매수 시작 검토"
    elif counts["warning"] >= 2: return "warning", "경계 구간 — 관망 유지"
    else: return "neutral", "중립 구간 — 지표 모니터링 지속"


# ─────────────────────────────────────────
# SIGNAL CARD HTML (스파크라인 제거)
# ─────────────────────────────────────────
def render_signal_card(title, ticker_hint, value, change, pct, signal, message, unit=""):
    color_map = {
        "danger":  ("#ef4444", "danger",  "status-danger"),
        "warning": ("#f59e0b", "warning", "status-warning"),
        "safe":    ("#22c55e", "safe",    "status-safe"),
        "neutral": ("#64748b", "neutral", "status-neutral"),
    }
    hex_color, card_cls, badge_cls = color_map.get(signal, color_map["neutral"])
    change_color = "#22c55e" if change >= 0 else "#ef4444"
    change_arrow = "▲" if change >= 0 else "▼"
    val_str = f"{value:,.2f}{unit}" if value is not None else "N/A"
    chg_str = f"{change_arrow} {abs(change):,.2f} ({abs(pct):.2f}%)" if value is not None else ""

    st.markdown(f"""
    <div class="signal-card {card_cls}">
        <div class="signal-label">{title} <span style="color:#2d3748">│</span> <span style="color:#2d3748;font-size:10px">{ticker_hint}</span></div>
        <div class="signal-value" style="color:{hex_color}">{val_str}</div>
        <div class="signal-change" style="color:{change_color}">{chg_str}</div>
        <span class="signal-status {badge_cls}">
            {message}
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.markdown("""
    <div class="dashboard-title">📊 거시경제 신호등 대시보드</div>
    <div class="dashboard-subtitle">MACRO INDICATOR SIGNAL MONITOR · 10년 장기 추세 적용</div>
    """, unsafe_allow_html=True)
with col_refresh:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

with st.spinner("실시간 데이터 및 10년치 히스토리 불러오는 중..."):
    market_data, last_update = fetch_market_data()
    fg_data = fetch_fear_greed()

# ─── Overall Signal Banner ───
all_signals = []
sig_info = {}
indicators = [
    ("WTI",  "WTI 원유",     "$",   ""),
    ("TNX",  "10년물 금리",  "",    "%"),
    ("VIX",  "VIX 공포지수", "",    ""),
    ("DXY",  "달러인덱스",   "",    ""),
]

for key, label, prefix, suffix in indicators:
    if market_data and market_data.get(key):
        d = market_data[key]
        sig, msg = get_signal(key, d["value"])
        all_signals.append(sig)
        sig_info[key] = (label, d, sig, msg, prefix, suffix)
    else:
        all_signals.append("neutral")
        sig_info[key] = (label, None, "neutral", "데이터 로딩 실패", prefix, suffix)

if fg_data:
    sig, msg = get_signal("FNG", fg_data["value"])
    all_signals.append(sig)

overall_sig, overall_msg = overall_signal(all_signals)
banner_color = {"danger": "#ef4444", "warning": "#f59e0b", "safe": "#22c55e", "neutral": "#64748b"}[overall_sig]

st.markdown(f"""
<div class="overall-banner overall-{overall_sig}">
    <div>
        <div style="font-size:13px;color:{banner_color};font-weight:600;letter-spacing:1px">종합 신호 판단</div>
        <div style="font-size:16px;color:#e2e8f0;font-weight:600">{overall_msg}</div>
    </div>
    <div style="margin-left:auto;text-align:right">
        <div style="font-size:10px;color:#475569">마지막 업데이트</div>
        <div style="font-size:11px;color:#64748b">{last_update}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── 5개 지표 카드 ───
st.markdown('<div class="section-header">핵심 거시 지표 모니터링</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col4, col5       = st.columns(2)
cols = [col1, col2, col3, col4, col5]

for i, (key, label, prefix, suffix) in enumerate(indicators):
    _, d, sig, msg, _, _ = sig_info[key]
    val, chg, pct = (d["value"], d["change"], d["pct"]) if d else (None, 0, 0)
    with cols[i]:
        render_signal_card(label, key, val, chg, pct, sig, msg, suffix)

if fg_data:
    sig_f, msg_f = get_signal("FNG", fg_data["value"])
    chg_f = fg_data["value"] - fg_data["prev"]
    pct_f = (chg_f / fg_data["prev"] * 100) if fg_data["prev"] else 0
    with cols[4]:
        render_signal_card("공포·탐욕 지수", "CNN FNG", fg_data["value"], chg_f, pct_f, sig_f, msg_f, "")


# ─── 신호등 요약 테이블 (Unpack 에러 수정 및 내용 수정 반영) ───
st.markdown('<div class="section-header">투자 판단 기준표</div>', unsafe_allow_html=True)

table_data = {
    "지표": ["WTI (원유)", "10년물 금리", "VIX (공포지수)", "달러인덱스 (DXY)", "공포·탐욕 지수"],
    "현재값": [],
    "🔴 시장 위험": ["$90 이상", "4.4% 이상", "30 이상 (투매 발생)", "105 이상", "25 이하 (극단 공포)"],
    "🟡 경계/관망": ["$85 ~ $90", "4.3% ~ 4.4%", "20 ~ 30", "103 ~ 105", "25~40 (공포) / 75↑ (탐욕)"],
    "🟢 시장 안정": ["$80 이하", "4.1% 이하", "15 미만", "103 미만", "40 ~ 75 (정상)"],
    "포트폴리오 행동": ["위험 시 현금 대기", "위험 시 기술주 비중 조절", "🔴 30 이상 시 역발상 매수", "위험 시 관망", "🔴 25 이하 시 역발상 매수"]
}

for key, label, prefix, suffix in indicators:
    # 수정 완료: 언패킹 개수를 정확히 6개로 맞춤
    _, d, _, _, _, _ = sig_info[key]
    if d:
        table_data["현재값"].append(f"{prefix}{d['value']:,.2f}{suffix}")
    else:
        table_data["현재값"].append("N/A")

if fg_data: table_data["현재값"].append(str(fg_data["value"]))
else: table_data["현재값"].append("N/A")

df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)


# ─── 10년 장기 추세선 (새롭게 추가된 대형 차트 영역) ───
st.markdown('<div class="section-header">📈 핵심 지표 10년 장기 추세선</div>', unsafe_allow_html=True)

chart_cols = st.columns(2)
chart_idx = 0

for key, label, prefix, suffix in indicators:
    if market_data and market_data.get(key) and market_data[key].get("df") is not None:
        df_hist = market_data[key]["df"]
        
        # Plotly 차트 생성
        fig = px.line(df_hist, y="Close", title=f"{label} ({key}) 10년 추이")
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="",
            yaxis_title=label,
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )
        fig.update_traces(line_color="#22c55e" if key == "WTI" else "#3b82f6" if key == "TNX" else "#ef4444" if key == "VIX" else "#a855f7", line_width=1.5)
        
        with chart_cols[chart_idx % 2]:
            st.plotly_chart(fig, use_container_width=True)
        chart_idx += 1
