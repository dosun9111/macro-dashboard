import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="거시경제 & 투자 컨설턴트 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CUSTOM CSS (두 앱의 디자인을 자연스럽게 통합)
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

/* 매크로 신호등 카드 */
.signal-card {
    background: #0f1117; border: 1px solid #1e2435; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 10px; position: relative; overflow: hidden;
}
.signal-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; border-radius: 4px 0 0 4px;
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

/* 종합 신호 배너 */
.overall-banner { border-radius: 10px; padding: 14px 22px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; font-family: 'IBM Plex Mono', monospace; }
.overall-danger  { background: #ef444411; border: 1px solid #ef444433; }
.overall-warning { background: #f59e0b11; border: 1px solid #f59e0b33; }
.overall-safe    { background: #22c55e11; border: 1px solid #22c55e33; }
.overall-neutral { background: #64748b11; border: 1px solid #64748b33; }

.section-header { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 3px; color: #475569; border-bottom: 1px solid #1e2435; padding-bottom: 6px; margin: 20px 0 12px 0; }
[data-testid="stDataFrame"] { border: 1px solid #1e2435 !important; border-radius: 8px !important; }
thead th { background: #0f1117 !important; color: #64748b !important; }

/* 종목별 포트폴리오 카드 (디자인 통합) */
.portfolio-card { background: #0f1117; border: 1px solid #1e2435; border-radius: 10px; padding: 20px; margin-bottom: 15px; }
.portfolio-title { font-size: 18px; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #1e2435; padding-bottom: 10px; display: flex; align-items: center; gap: 8px;}
.strategy-box { background: #1a202c; border-left: 4px solid #3b82f6; padding: 12px 15px; margin-top: 15px; border-radius: 4px; font-size: 13.5px; color: #e2e8f0; }
.target-price { font-size: 18px; font-weight: 700; color: #22c55e; font-family: 'IBM Plex Mono', monospace;}
.info-row { margin-bottom: 6px; font-size: 14.5px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_market_data():
    try:
        tickers = {"WTI": "CL=F", "TNX": "^TNX", "VIX": "^VIX", "DXY": "DX-Y.NYB"}
        results = {}
        for name, ticker in tickers.items():
            try:
                t = yf.Ticker(ticker)
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
                        "df": hist[["Close"]].copy()
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

@st.cache_data(ttl=300)
def fetch_stock_data():
    tickers = ["CRWD", "PANW", "GOOGL", "TSLA"]
    res = {}
    for t in tickers:
        try:
            hist = yf.Ticker(t).history(period="1d")
            res[t] = hist["Close"].iloc[-1] if not hist.empty else 0
        except: res[t] = 0
    return res


# ─────────────────────────────────────────
# SIGNAL LOGIC
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
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.markdown("### 👋 김도선 님, 환영합니다.")
st.sidebar.caption("ST인터내셔널 마케팅팀")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ 내 포트폴리오 설정")
st.sidebar.markdown("<span style='font-size:13px; color:#94a3b8'>정확한 물타기 타점 계산을 위해 현재 평단가를 입력하세요.</span>", unsafe_allow_html=True)
avg_googl = st.sidebar.number_input("구글(GOOGL) 평단가 ($)", value=145.0)
avg_tsla = st.sidebar.number_input("테슬라(TSLA) 평단가 ($)", value=190.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 현금 보유 현황 (목표)")
st.sidebar.markdown("""
<div style='font-size:14px; color:#cbd5e1'>
• <b>투입 대기 (신규):</b> 320만 원<br>
• <b>화학주 익절 대기:</b> 약 350만 원
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────
col_title, col_refresh = st.columns([6, 1])
with col_title:
    st.markdown("""
    <div style="font-size:26px; font-weight:700; margin-bottom:4px;">📊 거시경제 및 개인 투자 전략 대시보드</div>
    <div style="font-size:13px; color:#64748b; margin-bottom:20px; font-family:'IBM Plex Mono', monospace;">
    MACRO INDICATOR SIGNAL MONITOR & PORTFOLIO STRATEGY TERMINAL
    </div>
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
    stocks = fetch_stock_data()

# ─── TABS ───
tab1, tab2 = st.tabs(["📊 1. 거시경제 신호등 (Macro 10년 장기 추세)", "🎯 2. 종목별 방어/매수 전략 (Micro Portfolio)"])

# ==========================================
# TAB 1: MACRO DASHBOARD
# ==========================================
with tab1:
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

    # ─── 신호등 요약 테이블 ───
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
        _, d, _, _, _, _ = sig_info[key]
        if d: table_data["현재값"].append(f"{prefix}{d['value']:,.2f}{suffix}")
        else: table_data["현재값"].append("N/A")

    if fg_data: table_data["현재값"].append(str(fg_data["value"]))
    else: table_data["현재값"].append("N/A")

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ─── 10년 장기 추세선 ───
    st.markdown('<div class="section-header">📈 핵심 지표 10년 장기 추세선</div>', unsafe_allow_html=True)

    chart_cols = st.columns(2)
    chart_idx = 0

    for key, label, prefix, suffix in indicators:
        if market_data and market_data.get(key) and market_data[key].get("df") is not None:
            df_hist = market_data[key]["df"]
            fig = px.line(df_hist, y="Close", title=f"{label} ({key}) 10년 추이")
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="", yaxis_title=label, height=350, margin=dict(l=0, r=0, t=40, b=0), showlegend=False
            )
            fig.update_traces(line_color="#22c55e" if key == "WTI" else "#3b82f6" if key == "TNX" else "#ef4444" if key == "VIX" else "#a855f7", line_width=1.5)
            
            with chart_cols[chart_idx % 2]:
                st.plotly_chart(fig, use_container_width=True)
            chart_idx += 1


# ==========================================
# TAB 2: MICRO STRATEGY (다크 테마 디자인 융합)
# ==========================================
with tab2:
    st.markdown('<div class="section-header">🛡️ 기존 우량주 방어선 (물타기 타점 계산기)</div>', unsafe_allow_html=True)
    st.info("💡 사이드바에 입력하신 평단가 대비 **수익률이 특정 구간(-10%, -15% 등)에 도달했을 때만** 기계적으로 추가 매수합니다.")
    
    col_g, col_t = st.columns(2)
    
    # 구글 전략 카드
    with col_g:
        current_googl = stocks.get("GOOGL", 0)
        ret_googl = ((current_googl - avg_googl) / avg_googl) * 100 if avg_googl else 0
        ret_color = "#22c55e" if ret_googl > 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="portfolio-card">
            <div class="portfolio-title">🔵 Alphabet A (GOOGL)</div>
            <div class="info-row">현재가: <b style="font-family:'IBM Plex Mono', monospace; font-size:16px;">${current_googl:.2f}</b></div>
            <div class="info-row" style="color:#94a3b8">내 평단가: <span style="font-family:'IBM Plex Mono', monospace;">${avg_googl:.2f}</span> / 수익률: <span style='color:{ret_color}; font-weight:600;'>{ret_googl:.2f}%</span></div>
            <div style="margin: 15px 0; border-top: 1px dashed #1e2435;"></div>
            <div class="info-row"><b>1차 방어선 (-10% 구간):</b> <span class="target-price">${avg_googl * 0.90:.2f}</span> 부근</div>
            <div class="info-row"><b>2차 방어선 (-15% 구간):</b> <span class="target-price">${avg_googl * 0.85:.2f}</span> 부근</div>
            <div class="strategy-box">
                <b>🤖 컨설턴트 지침:</b> 현금 창출력이 압도적이므로 손절 금지. 위 타점에 도달하지 않으면 <b>절대 추가 매수(물타기)하지 말고 대기</b>하세요. 타점 도달 시 확보한 현금의 30%를 투입합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 테슬라 전략 카드
    with col_t:
        current_tsla = stocks.get("TSLA", 0)
        ret_tsla = ((current_tsla - avg_tsla) / avg_tsla) * 100 if avg_tsla else 0
        ret_color = "#22c55e" if ret_tsla > 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="portfolio-card">
            <div class="portfolio-title">🔴 Tesla (TSLA)</div>
            <div class="info-row">현재가: <b style="font-family:'IBM Plex Mono', monospace; font-size:16px;">${current_tsla:.2f}</b></div>
            <div class="info-row" style="color:#94a3b8">내 평단가: <span style="font-family:'IBM Plex Mono', monospace;">${avg_tsla:.2f}</span> / 수익률: <span style='color:{ret_color}; font-weight:600;'>{ret_tsla:.2f}%</span></div>
            <div style="margin: 15px 0; border-top: 1px dashed #1e2435;"></div>
            <div class="info-row"><b>1차 방어선 (-15% 구간):</b> <span class="target-price">${avg_tsla * 0.85:.2f}</span> 부근</div>
            <div class="info-row"><b>2차 방어선 (-25% 패닉셀):</b> <span class="target-price">${avg_tsla * 0.75:.2f}</span> 부근</div>
            <div class="strategy-box">
                <b>🤖 컨설턴트 지침:</b> 변동성이 매우 크므로 방어선을 깊게 잡았습니다. 어설픈 하락에 물 타지 마십시오. Macro 탭의 VIX 지수가 30을 넘기며 투매가 나올 때 현금을 과감히 투입합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:30px;">🚀 신규 위성 자산 (사이버 보안주 진입 타점)</div>', unsafe_allow_html=True)
    
    col_c, col_p = st.columns(2)
    
    # 크라우드스트라이크 전략 카드
    with col_c:
        current_crwd = stocks.get("CRWD", 0)
        st.markdown(f"""
        <div class="portfolio-card">
            <div class="portfolio-title">🦅 CrowdStrike (CRWD)</div>
            <div class="info-row">현재가: <b style="font-family:'IBM Plex Mono', monospace; font-size:16px;">${current_crwd:.2f}</b></div>
            <div style="margin: 15px 0; border-top: 1px dashed #1e2435;"></div>
            <div class="info-row"><b>1차 매수 (정찰병):</b> <span class="target-price" style="font-size:15px; color:#f8fafc;">현재가 1주 매수</span></div>
            <div class="info-row"><b>2차 매수 (지지선 대기):</b> <span class="target-price">$345.00</span> 부근 예약 매수</div>
            <div class="strategy-box">
                <b>🤖 컨설턴트 지침:</b> 고점 대비 많이 하락했으나 실적 발표 변동성이 남았습니다. 신규 자금 100만 원 중 절반만 현재가에 진입하고, 나머지는 $345 지지선에 그물망을 쳐둡니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 팔로알토 전략 카드
    with col_p:
        current_panw = stocks.get("PANW", 0)
        st.markdown(f"""
        <div class="portfolio-card">
            <div class="portfolio-title">🛡️ Palo Alto Networks (PANW)</div>
            <div class="info-row">현재가: <b style="font-family:'IBM Plex Mono', monospace; font-size:16px;">${current_panw:.2f}</b></div>
            <div style="margin: 15px 0; border-top: 1px dashed #1e2435;"></div>
            <div class="info-row"><b>1차 매수 (정찰병):</b> <span class="target-price" style="font-size:15px; color:#f8fafc;">현재가 2주 매수</span></div>
            <div class="info-row"><b>2차 매수 (쌍바닥 대기):</b> <span class="target-price">$140.00</span> 부근 예약 매수</div>
            <div class="strategy-box">
                <b>🤖 컨설턴트 지침:</b> $140 부근이 매우 강력한 지지선입니다. 현재가에 일부 진입하여 상승 시 소외되지 않도록 하고, 시장이 무너지면 $140에 대규모로 담아 평단가를 낮춥니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
