import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
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
# CUSTOM CSS  (Bloomberg-dark terminal feel)
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

/* Sidebar */
[data-testid="stSidebar"] { background: #0f1117 !important; border-right: 1px solid #1e2435; }

/* Cards */
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

.signal-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 4px;
}
.signal-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    line-height: 1.1;
}
.signal-change {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    margin-top: 4px;
}
.signal-status {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 8px;
    font-family: 'IBM Plex Mono', monospace;
}
.status-danger  { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
.status-warning { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
.status-safe    { background: #22c55e22; color: #22c55e; border: 1px solid #22c55e44; }
.status-neutral { background: #64748b22; color: #94a3b8; border: 1px solid #64748b44; }

/* Signal light */
.signal-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    vertical-align: middle;
}
.dot-danger  { background: #ef4444; box-shadow: 0 0 8px #ef4444; animation: pulse-red 1.5s infinite; }
.dot-warning { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; animation: pulse-yellow 1.5s infinite; }
.dot-safe    { background: #22c55e; box-shadow: 0 0 8px #22c55e; }
@keyframes pulse-red    { 0%,100%{opacity:1} 50%{opacity:0.4} }
@keyframes pulse-yellow { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Title area */
.dashboard-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #e2e8f0;
    text-transform: uppercase;
}
.dashboard-subtitle {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: #475569;
    margin-top: 2px;
    letter-spacing: 1px;
}
.last-update {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #475569;
}

/* Overall signal banner */
.overall-banner {
    border-radius: 10px;
    padding: 14px 22px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'IBM Plex Mono', monospace;
}
.overall-danger  { background: #ef444411; border: 1px solid #ef444433; }
.overall-warning { background: #f59e0b11; border: 1px solid #f59e0b33; }
.overall-safe    { background: #22c55e11; border: 1px solid #22c55e33; }

/* Section headers */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #475569;
    border-bottom: 1px solid #1e2435;
    padding-bottom: 6px;
    margin: 20px 0 12px 0;
}

/* Table styling */
[data-testid="stDataFrame"] { border: 1px solid #1e2435 !important; border-radius: 8px !important; }
thead th { background: #0f1117 !important; color: #64748b !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; }
tbody td { font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }

/* Plotly charts background */
.js-plotly-plot .plotly { background: transparent !important; }

button[kind="primary"] {
    background: #1e2435 !important;
    color: #e2e8f0 !important;
    border: 1px solid #2d3748 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 1px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────
def hex_to_rgba(hex_color, alpha=0.15):
    """HEX 색상을 RGBA 문자열로 변환하여 Plotly fillcolor 에러를 방지합니다."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{alpha})"
    return hex_color

# ─────────────────────────────────────────
# DATA FETCHING (Yahoo Finance via yfinance)
# ─────────────────────────────────────────
@st.cache_data(ttl=300)  # 5분 캐시
def fetch_market_data():
    """
    yfinance를 이용해 실시간에 가까운 시장 데이터를 가져옵니다.
    """
    try:
        import yfinance as yf

        tickers = {
            "WTI":    "CL=F",    # WTI 원유 선물
            "TNX":    "^TNX",    # 미 10년물 금리
            "VIX":    "^VIX",    # VIX 공포지수
            "DXY":    "DX-Y.NYB", # 달러인덱스
        }

        results = {}
        for name, ticker in tickers.items():
            try:
                t = yf.Ticker(ticker)
                # 안정성을 위해 기간을 7일로 늘리고, 결측치(NaN)를 제거합니다.
                hist = t.history(period="7d", interval="1d")
                
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
                        "hist": hist["Close"].tolist(),
                        "dates": [str(d.date()) for d in hist.index],
                    }
                elif len(hist) == 1:
                    current = hist["Close"].iloc[-1]
                    results[name] = {
                        "value": round(current, 2),
                        "change": 0,
                        "pct": 0,
                        "hist": hist["Close"].tolist(),
                        "dates": [str(d.date()) for d in hist.index],
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
    """CNN Fear & Greed Index (alternative.me API)"""
    try:
        r = requests.get("https://fear-and-greed-index.p.rapidapi.com/v1/fgi", timeout=5)
    except Exception:
        pass
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=2", timeout=5)
        data = r.json()["data"]
        current = int(data[0]["value"])
        prev    = int(data[1]["value"]) if len(data) > 1 else current
        label   = data[0]["value_classification"]
        return {"value": current, "prev": prev, "label": label}
    except Exception:
        return None


# ─────────────────────────────────────────
# SIGNAL LOGIC
# ─────────────────────────────────────────
def get_signal(indicator, value):
    if value is None:
        return "neutral", "데이터 없음"

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
        # 수정: VIX가 30 이상이면 '시장'은 극도 위험(danger)이나 '행동'은 매수
        if value >= 30:   return "danger",  "🔴 극단 공포 — 분할 매수 개시!"
        elif value >= 20: return "warning", "🟡 변동성 확대 — 경계"
        elif value < 15:  return "safe",    "🟢 안정 — 평온 구간"
        else:             return "neutral", "⚪ 관찰 — 정상 범위"

    if indicator == "DXY":
        if value >= 105:   return "danger",  "🔴 강달러 — 빅테크 실적 압박"
        elif value >= 103: return "warning", "🟡 달러 강세 — 주의"
        else:              return "safe",    "🟢 약달러 — 기술주 우호적"

    if indicator == "FNG":
        # 수정: 25 이하면 '시장'은 극도 위험(danger)이나 '행동'은 매수
        if value <= 25:   return "danger",  "🔴 극단 공포 — 현금 투입!"
        elif value <= 40: return "warning", "🟡 공포 — 투심 위축"
        elif value >= 75: return "warning", "🟡 극단 탐욕 — 신규 매수 자제" # 탐욕도 warning으로 변경
        else:             return "safe",    "🟢 정상 — 펀더멘털 집중"

    return "neutral", "—"


def overall_signal(signals):
    counts = {"danger": 0, "warning": 0, "safe": 0, "neutral": 0}
    for s in signals:
        counts[s] = counts.get(s, 0) + 1
    if counts["danger"] >= 2:
        return "danger",  "위험 구간 — 현금 비중 확대 권고"
    elif counts["safe"] >= 3:
        return "safe",    "기회 구간 — 분할 매수 시작 검토"
    elif counts["warning"] >= 2:
        return "warning", "경계 구간 — 관망 유지"
    else:
        return "neutral", "중립 구간 — 지표 모니터링 지속"


def sparkline(hist_values, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=hist_values,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=hex_to_rgba(color, 0.15),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=50,
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────
# SIGNAL CARD HTML
# ─────────────────────────────────────────
def render_signal_card(title, ticker_hint, value, change, pct, signal, message, unit="", hist=None):
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

    dot_cls = f"dot-{card_cls}"

    st.markdown(f"""
    <div class="signal-card {card_cls}">
        <div class="signal-label">{title} <span style="color:#2d3748">│</span> <span style="color:#2d3748;font-size:10px">{ticker_hint}</span></div>
        <div class="signal-value" style="color:{hex_color}">{val_str}</div>
        <div class="signal-change" style="color:{change_color}">{chg_str}</div>
        <span class="signal-status {badge_cls}">
            <span class="signal-dot {dot_cls}"></span>{message}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if hist and len(hist) > 1:
        fig = sparkline(hist, hex_color)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────
# Header
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.markdown("""
    <div class="dashboard-title">📊 거시경제 신호등 대시보드</div>
    <div class="dashboard-subtitle">MACRO INDICATOR SIGNAL MONITOR · 빅테크 / 테슬라 포트폴리오 최적화</div>
    """, unsafe_allow_html=True)
with col_refresh:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# Fetch
with st.spinner("실시간 데이터 불러오는 중..."):
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
banner_cls   = f"overall-{overall_sig}"
icon_map     = {"danger": "🔴", "warning": "🟡", "safe": "🟢", "neutral": "⚪"}

st.markdown(f"""
<div class="overall-banner {banner_cls}">
    <span style="font-size:24px">{icon_map[overall_sig]}</span>
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
card_data = []

for key, label, prefix, suffix in indicators:
    _, d, sig, msg, _, _ = sig_info[key]
    if d:
        card_data.append((label, key, d["value"], d["change"], d["pct"], sig, msg, suffix, d.get("hist")))
    else:
        card_data.append((label, key, None, 0, 0, "neutral", "데이터 없음", suffix, None))

# FNG
if fg_data:
    sig_f, msg_f = get_signal("FNG", fg_data["value"])
    change_f = fg_data["value"] - fg_data["prev"]
    pct_f    = (change_f / fg_data["prev"] * 100) if fg_data["prev"] else 0
    card_data.append(("공포·탐욕 지수", "CNN FNG", fg_data["value"], change_f, pct_f, sig_f, msg_f, "", None))
else:
    card_data.append(("공포·탐욕 지수", "CNN FNG", None, 0, 0, "neutral", "데이터 없음", "", None))

for i, (title, ticker, val, chg, pct, sig, msg, unit, hist) in enumerate(card_data):
    with cols[i]:
        render_signal_card(title, ticker, val, chg, pct, sig, msg, unit, hist)

# ─── 신호등 요약 테이블 ───
st.markdown('<div class="section-header">투자 판단 기준표</div>', unsafe_allow_html=True)

table_data = {
    "지표":       ["WTI (원유)",      "10년물 금리",         "VIX (공포지수)",         "달러인덱스 (DXY)",      "공포·탐욕 지수"],
    "현재값":      [],
    "🔴 시장 위험": ["$90 이상",        "4.4% 이상",           "30 이상 (투매 발생)",      "105 이상",              "25 이하 (극단 공포)"],
    "🟡 경계/관망": ["$85 ~ $90",       "4.3% ~ 4.4%",         "20 ~ 30",                "103 ~ 105",             "25~40 (공포) / 75↑ (탐욕)"],
    "🟢 시장 안정": ["$80 이하",        "4.1% 이하",           "15 미만",                "103 미만",              "40 ~ 75 (정상)"],
    "포트폴리오 행동": [
        "위험 시 현금 대기",
        "위험 시 기술주 비중 조절",
        "🔴 30 이상 시 역발상 매수",
        "위험 시 관망",
        "🔴 25 이하 시 역발상 매수"
    ],
}

for key, label, prefix, suffix in indicators:
    _, d, _, _, _, _, _ = sig_info[key]
    if d:
        table_data["현재값"].append(f"{prefix}{d['value']:,.2f}{suffix}")
    else:
        table_data["현재값"].append("N/A")

if fg_data:
    table_data["현재값"].append(str(fg_data["value"]))
else:
    table_data["현재값"].append("N/A")

df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

# ─── 투자 행동 가이드 ───
st.markdown('<div class="section-header">현재 상황별 행동 가이드</div>', unsafe_allow_html=True)

guide_col1, guide_col2, guide_col3 = st.columns(3)

with guide_col1:
    st.markdown("""
    <div class="signal-card danger">
        <div class="signal-label">🔴 위험 신호 시 행동</div>
        <div style="font-size:13px;color:#e2e8f0;line-height:1.8;margin-top:8px">
        • 신규 매수 <b>중단</b><br>
        • 현금 비중 확대 (예수금 확보)<br>
        • 손실 종목 손절 검토<br>
        • WTI $90 / TNX 4.5% 이상이면<br>
        &nbsp;&nbsp;즉시 현금화 비중 확대
        </div>
    </div>
    """, unsafe_allow_html=True)

with guide_col2:
    st.markdown("""
    <div class="signal-card warning">
        <div class="signal-label">🟡 경계 신호 시 행동</div>
        <div style="font-size:13px;color:#e2e8f0;line-height:1.8;margin-top:8px">
        • 관망 유지 (포지션 유지)<br>
        • 현금 350만원 + 예수금 320만원<br>
        &nbsp;&nbsp;투입 대기<br>
        • VIX / FNG 지수 일일 확인<br>
        • 분할매수 1차 라인 설정
        </div>
    </div>
    """, unsafe_allow_html=True)

with guide_col3:
    st.markdown("""
    <div class="signal-card safe">
        <div class="signal-label">🟢 기회 신호 시 행동</div>
        <div style="font-size:13px;color:#e2e8f0;line-height:1.8;margin-top:8px">
        • VIX 30+ / FNG 25 이하면<br>
        &nbsp;&nbsp;<b>현금 1차 투입 (30%)</b><br>
        • 구글 (GOOGL) 분할 매수<br>
        • 테슬라 (TSLA) 분할 매수<br>
        • 하락 추가 시 2·3차 매수
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top:30px;padding-top:16px;border-top:1px solid #1e2435;
     font-family:'IBM Plex Mono',monospace;font-size:10px;color:#2d3748;text-align:center;letter-spacing:1px">
MACRO SIGNAL DASHBOARD · FOR PERSONAL INVESTMENT REFERENCE ONLY · NOT FINANCIAL ADVICE<br>
DATA SOURCE: Yahoo Finance · CNN Fear &amp; Greed Index (Alternative.me API) · Auto-refresh every 5 min
</div>
""", unsafe_allow_html=True)
