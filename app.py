import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf

# ─────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────
st.set_page_config(page_title="개인 투자 컨설턴트 대시보드", page_icon="💼", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color: #0a0c10 !important; color: #e2e8f0 !important; font-family: 'IBM Plex Sans', sans-serif; }
.card { background: #0f1117; border: 1px solid #1e2435; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
.strategy-box { background: #1a202c; border-left: 4px solid #3b82f6; padding: 10px 15px; margin-top: 10px; border-radius: 4px; font-size: 13px; color: #cbd5e1; }
.target-price { font-size: 18px; font-weight: bold; color: #22c55e; }
.danger-text { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATA FETCHING FUNCTIONS
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_macro_data():
    tickers = {"WTI": "CL=F", "TNX": "^TNX", "VIX": "^VIX", "DXY": "DX-Y.NYB"}
    res = {}
    for name, t in tickers.items():
        try:
            hist = yf.Ticker(t).history(period="2d")
            res[name] = hist["Close"].iloc[-1] if not hist.empty else None
        except: res[name] = None
    return res

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
# SIDEBAR: USER SETTINGS (내 평단가 입력)
# ─────────────────────────────────────────
st.sidebar.markdown("### ⚙️ 내 포트폴리오 설정")
st.sidebar.markdown("정확한 물타기 타점 계산을 위해 현재 평단가를 입력하세요.")
avg_googl = st.sidebar.number_input("구글(GOOGL) 평단가 ($)", value=145.0)
avg_tsla = st.sidebar.number_input("테슬라(TSLA) 평단가 ($)", value=190.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 현금 보유 현황 (목표)")
st.sidebar.markdown("- **투입 대기 (신규):** 320만 원\n- **화학주 익절 대기:** 약 350만 원")

# ─────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────
st.title("💼 개인 투자 컨설턴트 터미널")
st.markdown("매크로 지표 분석 및 내 포트폴리오 기계적 대응 가이드")

tab1, tab2 = st.tabs(["📊 1. 거시경제 신호등 (Macro)", "🎯 2. 종목별 방어/매수 전략 (Micro)"])

# ====== TAB 1: 거시경제 ======
with tab1:
    macro = fetch_macro_data()
    col1, col2, col3, col4 = st.columns(4)
    
    # 간단한 매크로 신호등 렌더링 (이전 코드의 핵심 요약판)
    with col1:
        st.markdown(f"<div class='card'><b>🛢️ WTI 원유</b><br><span style='font-size:24px'>${macro.get('WTI', 0):.2f}</span><br><span style='font-size:12px;color:#94a3b8'>$85 돌파 시 시장 위험</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><b>📈 10년물 금리</b><br><span style='font-size:24px'>{macro.get('TNX', 0):.2f}%</span><br><span style='font-size:12px;color:#94a3b8'>4.4% 돌파 시 기술주 주의</span></div>", unsafe_allow_html=True)
    with col3:
        vix_val = macro.get('VIX', 0)
        vix_color = "#ef4444" if vix_val >= 25 else "#22c55e"
        st.markdown(f"<div class='card'><b>😨 VIX 공포지수</b><br><span style='font-size:24px;color:{vix_color}'>{vix_val:.2f}</span><br><span style='font-size:12px;color:#94a3b8'>30 이상 시 '현금 투입' 신호</span></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card'><b>💵 달러 인덱스</b><br><span style='font-size:24px'>{macro.get('DXY', 0):.2f}</span><br><span style='font-size:12px;color:#94a3b8'>105 이상 시 빅테크 부담</span></div>", unsafe_allow_html=True)

# ====== TAB 2: 종목별 전략 ======
with tab2:
    stocks = fetch_stock_data()
    st.markdown("### 🛡️ 기존 우량주 방어선 (물타기 타점 계산기)")
    st.info("입력하신 평단가 대비 **수익률이 특정 구간(-10%, -15% 등)에 도달했을 때만** 기계적으로 추가 매수합니다.")
    
    col_g, col_t = st.columns(2)
    
    # 구글 전략 카드
    with col_g:
        current_googl = stocks.get("GOOGL", 0)
        ret_googl = ((current_googl - avg_googl) / avg_googl) * 100
        ret_color = "#22c55e" if ret_googl > 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="card">
            <h4>🔵 Alphabet A (GOOGL)</h4>
            현재가: <b>${current_googl:.2f}</b> (내 평단가: ${avg_googl:.2f} / <span style='color:{ret_color}'>{ret_googl:.2f}%</span>)
            <hr>
            <div><b>1차 방어선 (-10% 구간):</b> <span class="target-price">${avg_googl * 0.90:.2f}</span> 부근</div>
            <div><b>2차 방어선 (-15% 구간):</b> <span class="target-price">${avg_googl * 0.85:.2f}</span> 부근</div>
            <div class="strategy-box">
                <b>💡 컨설턴트 지침:</b> 현금 창출력이 압도적이므로 손절 금지. 위 타점에 도달하지 않으면 <b>절대 추가 매수(물타기)하지 말고 대기</b>하세요. 타점 도달 시 확보한 현금의 30%를 투입합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 테슬라 전략 카드
    with col_t:
        current_tsla = stocks.get("TSLA", 0)
        ret_tsla = ((current_tsla - avg_tsla) / avg_tsla) * 100
        ret_color = "#22c55e" if ret_tsla > 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="card">
            <h4>🔴 Tesla (TSLA)</h4>
            현재가: <b>${current_tsla:.2f}</b> (내 평단가: ${avg_tsla:.2f} / <span style='color:{ret_color}'>{ret_tsla:.2f}%</span>)
            <hr>
            <div><b>1차 방어선 (-15% 구간):</b> <span class="target-price">${avg_tsla * 0.85:.2f}</span> 부근</div>
            <div><b>2차 방어선 (-25% 패닉셀):</b> <span class="target-price">${avg_tsla * 0.75:.2f}</span> 부근</div>
            <div class="strategy-box">
                <b>💡 컨설턴트 지침:</b> 변동성이 매우 크므로 방어선을 깊게 잡았습니다. 어설픈 하락에 물 타지 마십시오. VIX 지수가 30을 넘기며 투매가 나올 때(2차 방어선) 현금을 과감히 투입합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>### 🚀 신규 위성 자산 (사이버 보안주 진입 타점)", unsafe_allow_html=True)
    
    col_c, col_p = st.columns(2)
    
    # 크라우드스트라이크 전략 카드
    with col_c:
        current_crwd = stocks.get("CRWD", 0)
        st.markdown(f"""
        <div class="card">
            <h4>🦅 CrowdStrike (CRWD)</h4>
            현재가: <b>${current_crwd:.2f}</b>
            <hr>
            <div><b>1차 매수 (정찰병):</b> <span class="target-price">현재가 1주</span></div>
            <div><b>2차 매수 (지지선 대기):</b> <span class="target-price">$345.00</span> 부근 예약 매수</div>
            <div class="strategy-box">
                <b>💡 컨설턴트 지침:</b> 고점 대비 많이 하락했으나 실적 발표 변동성이 남았습니다. 신규 자금 100만 원 중 절반만 현재가에 진입하고, 나머지는 $345 지지선에 그물망을 쳐둡니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 팔로알토 전략 카드
    with col_p:
        current_panw = stocks.get("PANW", 0)
        st.markdown(f"""
        <div class="card">
            <h4>🛡️ Palo Alto Networks (PANW)</h4>
            현재가: <b>${current_panw:.2f}</b>
            <hr>
            <div><b>1차 매수 (정찰병):</b> <span class="target-price">현재가 2주</span></div>
            <div><b>2차 매수 (쌍바닥 대기):</b> <span class="target-price">$140.00</span> 부근 예약 매수</div>
            <div class="strategy-box">
                <b>💡 컨설턴트 지침:</b> $140 부근이 매우 강력한 지지선입니다. 현재가에 일부 진입하여 상승 시 소외되지 않도록 하고, 시장이 무너지면 $140에 대규모로 담아 평단가를 낮춥니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
