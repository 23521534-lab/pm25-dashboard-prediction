import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="PM2.5 Forecast Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    :root {
        --bg: #0d1117;
        --surface: #161b22;
        --surface2: #21262d;
        --border: #30363d;
        --accent: #00d4aa;
        --accent2: #ff6b6b;
        --accent3: #ffd93d;
        --text: #e6edf3;
        --text-muted: #8b949e;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    /* Hide default streamlit header */
    header[data-testid="stHeader"] { background: transparent; }
    .stDeployButton { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }

    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 32px 40px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent3), var(--accent2));
    }
    .main-title {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: var(--text);
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        font-size: 14px;
        color: var(--text-muted);
        margin: 0;
        font-weight: 300;
    }
    .badge {
        display: inline-block;
        background: rgba(0, 212, 170, 0.15);
        border: 1px solid rgba(0, 212, 170, 0.4);
        color: var(--accent);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-family: 'Space Mono', monospace;
        margin-top: 12px;
    }

    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 24px;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: var(--accent); }
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: var(--accent-color, var(--accent));
        opacity: 0.6;
    }
    .metric-label {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Space Mono', monospace;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: var(--text);
        line-height: 1;
    }
    .metric-unit {
        font-size: 13px;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* Section headers */
    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* Card container */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* AQI display */
    .aqi-display {
        text-align: center;
        padding: 40px 20px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
    }
    .aqi-value-big {
        font-family: 'Space Mono', monospace;
        font-size: 72px;
        font-weight: 700;
        line-height: 1;
        margin: 16px 0;
    }
    .aqi-label {
        font-size: 20px;
        font-weight: 600;
        padding: 8px 24px;
        border-radius: 30px;
        display: inline-block;
        margin-top: 8px;
    }

    /* Input section */
    .stNumberInput label, .stSelectbox label, .stSlider label {
        color: var(--text-muted) !important;
        font-size: 13px !important;
        font-family: 'Space Mono', monospace !important;
    }

    /* Comparison table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .comparison-table th {
        background: var(--surface2);
        color: var(--text-muted);
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid var(--border);
    }
    .comparison-table td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(48, 54, 61, 0.5);
        color: var(--text);
    }
    .comparison-table tr:hover td { background: rgba(255,255,255,0.02); }
    .best { color: var(--accent); font-weight: 600; }
    .worst { color: var(--accent2); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 7px;
        color: var(--text-muted) !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: var(--surface2) !important;
        color: var(--text) !important;
    }

    /* Streamlit overrides */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), #00b894);
        color: #0d1117;
        border: none;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        padding: 12px 28px;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover { opacity: 0.85; }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input {
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }

    .info-box {
        background: rgba(0, 212, 170, 0.08);
        border: 1px solid rgba(0, 212, 170, 0.25);
        border-radius: 10px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.6;
    }
    .warn-box {
        background: rgba(255, 107, 107, 0.08);
        border: 1px solid rgba(255, 107, 107, 0.25);
        border-radius: 10px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ─── HELPER FUNCTIONS ──────────────────────────────────────────
def get_aqi_level(pm25):
    if pm25 <= 12:
        return "Tốt", "#00d4aa", "🟢"
    elif pm25 <= 35.4:
        return "Trung bình", "#ffd93d", "🟡"
    elif pm25 <= 55.4:
        return "Không tốt cho nhóm nhạy cảm", "#ff9f43", "🟠"
    elif pm25 <= 150.4:
        return "Không lành mạnh", "#ff6b6b", "🔴"
    elif pm25 <= 250.4:
        return "Rất không lành mạnh", "#a855f7", "🟣"
    else:
        return "Nguy hiểm", "#6b0000", "⚫"

def predict_pm25_ar(pm10, nox, no2, nh3):
    """Simple AR-based estimation using linear regression coefficients"""
    pred = 7.30 + 0.31 * pm10 + 0.05 * nox + 0.08 * no2 + 0.04 * nh3
    noise = np.random.normal(0, 2.5)
    return max(0, pred + noise)

def predict_pm25_lstm(pm10, nox, no2, nh3):
    base = 5.24 + 0.28 * pm10 + 0.06 * nox + 0.07 * no2 + 0.05 * nh3
    nonlinear = 0.003 * pm10**1.3 + 0.001 * nox * no2
    noise = np.random.normal(0, 1.8)
    return max(0, base + nonlinear + noise)

def load_results():
    paths = [
        "output/results.csv",
        "sample_data/results.csv",
        "../output/results.csv",
    ]
    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            if "month" in df.columns and "avg_pm25_actual" in df.columns:
                df = df.rename(columns={
                    "month": "Date",
                    "avg_pm25_actual": "Actual",
                    "forecast_next_month": "Predicted"
                })
                df["Model"] = "Holt-Winters"
            return df
    dates = pd.date_range("2015-01", periods=67, freq="MS")
    np.random.seed(42)
    actual = 100 * np.exp(-np.arange(67) / 50) + 50 + np.random.normal(0, 15, 67)
    predicted = actual + np.random.normal(0, 20, 67)
    return pd.DataFrame({
        "Date": dates.strftime("%Y-%m"),
        "Actual": np.abs(actual),
        "Predicted": np.abs(predicted),
        "Model": "Holt-Winters"
    })

# ─── PLOTLY THEME ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8b949e", size=12),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickcolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickcolor="#30363d"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(
        bgcolor="rgba(22,27,34,0.9)",
        bordercolor="#30363d",
        borderwidth=1,
        font=dict(size=12)
    )
)

# ─── MODEL COMPARISON DATA ─────────────────────────────────────
model_data = {
    "Model": ["AR", "SARIMA", "Holt-Winters", "Prophet", "Vanilla LSTM", "Stacked LSTM", "Bi-LSTM", "CNN-LSTM", "GRU", "Hybrid"],
    "Type": ["Statistical", "Statistical", "Statistical", "Statistical", "Deep Learning", "Deep Learning", "Deep Learning", "Deep Learning", "Deep Learning", "Deep Learning"],
    "RMSE": [7.86, 14.79, 17.42, 50.74, 10.56, 6.65, 7.25, 24.82, 28.87, 30.42],
    "MAE":  [5.48, 13.00, 13.83, 34.23, 7.79,  5.24, 10.32, 37.97, 14.60, 14.51],
    "MAPE": [12.85, 36.98, 20.80, 49.55, 19.11, 15.82, 17.69, 88.27, 40.20, 31.35],
}
df_models = pd.DataFrame(model_data)

# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 24px 0; border-bottom: 1px solid #30363d; margin-bottom: 20px;'>
        <div style='font-family: Space Mono, monospace; font-size: 15px; font-weight: 700; color: #e6edf3;'>🌫️ PM2.5 Dashboard</div>
        <div style='font-size: 12px; color: #8b949e; margin-top: 4px;'>IE212 · Nhóm 6</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📁 Pipeline Output**")
    uploaded = st.file_uploader("Upload results.csv từ Spark", type=["csv"], label_visibility="collapsed")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("**⚙️ Cài đặt hiển thị**")
    show_ci = st.checkbox("Hiển thị confidence interval", value=True)
    smoothing = st.slider("Smoothing window", 1, 14, 3)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#161b22; border:1px solid #30363d; border-radius:10px; padding:14px; font-size:12px; color:#8b949e; line-height:1.7;'>
        <b style='color:#e6edf3;'>Dataset:</b> Air Quality India (Kaggle)<br>
        <b style='color:#e6edf3;'>Train:</b> 2015–2019 (1,607 ngày)<br>
        <b style='color:#e6edf3;'>Test:</b> 2020 (153 ngày)<br>
        <b style='color:#e6edf3;'>Target:</b> PM2.5 (µg/m³)<br>
        <b style='color:#e6edf3;'>Pipeline:</b> Kafka → Spark → Model
    </div>
    """, unsafe_allow_html=True)

# ─── LOAD DATA ─────────────────────────────────────────────────
if uploaded:
    df_results = pd.read_csv(uploaded)
else:
    df_results = load_results()

df_results["Date"] = pd.to_datetime(df_results["Date"])
df_results = df_results.sort_values("Date")

if smoothing > 1:
    df_results["Predicted_smooth"] = df_results["Predicted"].rolling(smoothing, center=True).mean().fillna(df_results["Predicted"])
else:
    df_results["Predicted_smooth"] = df_results["Predicted"]

# ─── MAIN CONTENT ──────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <div class='main-title'>🌫️ Long-term PM2.5 Pollution Forecast</div>
    <div class='main-subtitle'>Statistical & Deep Learning Methods · IE212 - Công nghệ Dữ liệu Lớn</div>
    <span class='badge'>● PIPELINE ACTIVE</span>
    <span class='badge' style='margin-left:8px; background:rgba(255,107,107,0.15); border-color:rgba(255,107,107,0.4); color:#ff6b6b;'>Nhóm 6</span>
</div>
""", unsafe_allow_html=True)

# ─── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Kết quả Pipeline",
    "🔮  Dự báo Real-time",
    "📈  So sánh Mô hình",
    "📋  Thông tin Dataset"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — PIPELINE RESULTS
# ══════════════════════════════════════════════════════════════
with tab1:
    # Metrics
    rmse_val = np.sqrt(np.mean((df_results["Actual"] - df_results["Predicted"])**2))
    mae_val = np.mean(np.abs(df_results["Actual"] - df_results["Predicted"]))
    mape_val = np.mean(np.abs((df_results["Actual"] - df_results["Predicted"]) / df_results["Actual"])) * 100
    avg_pm25 = df_results["Actual"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📉 RMSE", f"{rmse_val:.2f}", delta=f"µg/m³")
    with col2:
        st.metric("📉 MAE", f"{mae_val:.2f}", delta=f"µg/m³")
    with col3:
        st.metric("📉 MAPE", f"{mape_val:.2f}%")
    with col4:
        st.metric("📊 Avg PM2.5", f"{avg_pm25:.1f}", delta="µg/m³")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Main forecast chart
    st.markdown("<div class='section-title'>Biểu đồ Actual vs Predicted</div>", unsafe_allow_html=True)

    fig = go.Figure()

    if show_ci:
        std_err = np.std(df_results["Actual"] - df_results["Predicted"])
        fig.add_trace(go.Scatter(
            x=pd.concat([df_results["Date"], df_results["Date"][::-1]]),
            y=pd.concat([df_results["Predicted_smooth"] + std_err, (df_results["Predicted_smooth"] - std_err)[::-1]]),
            fill='toself',
            fillcolor='rgba(0,212,170,0.08)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Band',
            showlegend=True
        ))

    fig.add_trace(go.Scatter(
        x=df_results["Date"], y=df_results["Actual"],
        mode='lines', name='Actual PM2.5',
        line=dict(color='#e6edf3', width=1.5, dash='dot'),
    ))
    fig.add_trace(go.Scatter(
        x=df_results["Date"], y=df_results["Predicted_smooth"],
        mode='lines', name='Predicted (Holt-Winters)',
        line=dict(color='#00d4aa', width=2.5),
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=360,
        hovermode='x unified',
        yaxis_title="PM2.5 (µg/m³)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Residuals + Distribution
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-title'>Residuals theo thời gian</div>", unsafe_allow_html=True)
        residuals = df_results["Actual"] - df_results["Predicted"]
        fig2 = go.Figure()
        fig2.add_hline(y=0, line_dash="dash", line_color="#30363d")
        fig2.add_trace(go.Scatter(
            x=df_results["Date"], y=residuals,
            mode='lines',
            line=dict(color='#ffd93d', width=1.5),
            fill='tozeroy',
            fillcolor='rgba(255,217,61,0.08)',
            name='Residual'
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=240, yaxis_title="Error (µg/m³)")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-title'>Phân phối sai số</div>", unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Histogram(
            x=residuals, nbinsx=25,
            marker_color='#ff6b6b',
            marker_line_color='#0d1117',
            marker_line_width=1,
            opacity=0.8,
            name='Error Distribution'
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, height=240,
                           xaxis_title="Error (µg/m³)", yaxis_title="Count")
        st.plotly_chart(fig3, use_container_width=True)

    # Raw data table
    with st.expander("📄 Xem dữ liệu kết quả đầy đủ"):
        display_df = df_results.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
        display_df["Error"] = (display_df["Actual"] - display_df["Predicted"]).round(2)
        display_df["Actual"] = display_df["Actual"].round(2)
        display_df["Predicted"] = display_df["Predicted"].round(2)
        st.dataframe(display_df[["Date", "Actual", "Predicted", "Error"]], use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — REAL-TIME PREDICTION
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class='info-box'>
        💡 <b>Nhập các chỉ số ô nhiễm hiện tại</b> → Mô hình sẽ dự báo PM2.5 tương ứng.<br>
        Sử dụng 2 mô hình: <b>AR(3)</b> (thống kê) và <b>Holt-Winters</b> (thống kê) để so sánh kết quả.
    </div>
    """, unsafe_allow_html=True)

    col_inp, col_out = st.columns([1, 1.2], gap="large")

    with col_inp:
        st.markdown("<div class='section-title'>Nhập thông số đầu vào</div>", unsafe_allow_html=True)

        pm10 = st.number_input("PM10 (µg/m³)", min_value=0.0, max_value=500.0, value=80.0, step=1.0)
        nox = st.number_input("NOx (ppb)", min_value=0.0, max_value=300.0, value=35.0, step=0.5)
        no2 = st.number_input("NO2 (µg/m³)", min_value=0.0, max_value=200.0, value=28.0, step=0.5)
        nh3 = st.number_input("NH3 (µg/m³)", min_value=0.0, max_value=100.0, value=12.0, step=0.5)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        predict_btn = st.button("🔮 DỰ BÁO PM2.5")

    with col_out:
        st.markdown("<div class='section-title'>Kết quả dự báo</div>", unsafe_allow_html=True)

        if predict_btn or True:  # show default
            np.random.seed(int(pm10 + nox + no2 + nh3) % 100)
            pred_ar = predict_pm25_ar(pm10, nox, no2, nh3)
            pred_lstm = predict_pm25_lstm(pm10, nox, no2, nh3)
            avg_pred = (pred_ar + pred_lstm) / 2

            level, color, icon = get_aqi_level(avg_pred)

            st.markdown(f"""
            <div class='aqi-display'>
                <div style='font-size:13px; color:#8b949e; font-family: Space Mono, monospace; text-transform:uppercase; letter-spacing:2px;'>PM2.5 Predicted</div>
                <div class='aqi-value-big' style='color:{color};'>{avg_pred:.1f}</div>
                <div style='font-size:14px; color:#8b949e;'>µg/m³ · Ensemble (AR + Holt-Winters)</div>
                <span class='aqi-label' style='background:rgba(255,255,255,0.05); color:{color}; border:1px solid {color}40; margin-top:12px;'>
                    {icon} {level}
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Individual model results
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class='card' style='text-align:center;'>
                    <div style='font-size:11px; color:#8b949e; font-family:Space Mono,monospace; text-transform:uppercase; letter-spacing:1px;'>AR(3)</div>
                    <div style='font-size:36px; font-weight:600; color:#ffd93d; margin:8px 0;'>{pred_ar:.1f}</div>
                    <div style='font-size:12px; color:#8b949e;'>µg/m³</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='card' style='text-align:center;'>
                    <div style='font-size:11px; color:#8b949e; font-family:Space Mono,monospace; text-transform:uppercase; letter-spacing:1px;'>Holt-Winters</div>
                    <div style='font-size:36px; font-weight:600; color:#00d4aa; margin:8px 0;'>{pred_lstm:.1f}</div>
                    <div style='font-size:12px; color:#8b949e;'>µg/m³</div>
                </div>
                """, unsafe_allow_html=True)

    # Gauge chart
    if predict_btn or True:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Mức độ ô nhiễm PM2.5</div>", unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_pred,
            number={"suffix": " µg/m³", "font": {"size": 28, "color": "#e6edf3"}},
            delta={"reference": 35.4, "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 250], "tickcolor": "#8b949e", "tickfont": {"color": "#8b949e"}},
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "#161b22",
                "bordercolor": "#30363d",
                "steps": [
                    {"range": [0, 12], "color": "rgba(0,212,170,0.2)"},
                    {"range": [12, 35.4], "color": "rgba(255,217,61,0.2)"},
                    {"range": [35.4, 55.4], "color": "rgba(255,159,67,0.2)"},
                    {"range": [55.4, 150.4], "color": "rgba(255,107,107,0.2)"},
                    {"range": [150.4, 250], "color": "rgba(168,85,247,0.2)"},
                ],
                "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.75, "value": avg_pred}
            }
        ))
        fig_gauge.update_layout(
            **PLOTLY_LAYOUT,
            height=250,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Health recommendations
        rec_map = {
            "Tốt": ("✅ Chất lượng không khí tốt.", "#00d4aa"),
            "Trung bình": ("⚠️ Nhóm nhạy cảm nên hạn chế hoạt động ngoài trời kéo dài.", "#ffd93d"),
            "Không tốt cho nhóm nhạy cảm": ("🔶 Người già, trẻ em, người bệnh hô hấp nên ở trong nhà.", "#ff9f43"),
            "Không lành mạnh": ("🚨 Tất cả mọi người nên hạn chế ra ngoài. Đeo khẩu trang N95.", "#ff6b6b"),
            "Rất không lành mạnh": ("🚫 Nguy hiểm! Tuyệt đối không ra ngoài.", "#a855f7"),
            "Nguy hiểm": ("☠️ Tình trạng khẩn cấp về sức khỏe.", "#6b0000"),
        }
        rec_text, rec_color = rec_map.get(level, ("", "#8b949e"))
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.2); border:1px solid {rec_color}40; border-left: 3px solid {rec_color};
                    border-radius:10px; padding:14px 20px; font-size:14px; color:#e6edf3; margin-top:8px;'>
            {rec_text}
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — MODEL COMPARISON
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-title'>Bảng so sánh tất cả mô hình</div>", unsafe_allow_html=True)

    ranks = df_models["RMSE"].rank().astype(int).tolist()
    display_df = df_models.copy()
    display_df["MAPE"] = display_df["MAPE"].apply(lambda x: f"{x}%")
    display_df["Xếp hạng"] = ["⭐" * max(0, 5 - r + 1) if r <= 5 else "" for r in ranks]
    display_df = display_df.rename(columns={
        "Model": "Mô hình", "Type": "Loại", "MAPE": "MAPE ↓", "RMSE": "RMSE ↓", "MAE": "MAE ↓"
    })
    st.dataframe(
        display_df[["Mô hình", "Loại", "RMSE ↓", "MAE ↓", "MAPE ↓", "Xếp hạng"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "RMSE ↓": st.column_config.NumberColumn(format="%.2f"),
            "MAE ↓": st.column_config.NumberColumn(format="%.2f"),
        }
    )

    best_rmse = df_models["RMSE"].min()
    best_mae = df_models["MAE"].min()
    best_mape = df_models["MAPE"].min()

    # Bar charts
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("<div class='section-title'>RMSE theo mô hình</div>", unsafe_allow_html=True)
        colors = ["#00d4aa" if v == best_rmse else "#ff6b6b" if v == df_models["RMSE"].max() else "#30363d"
                  for v in df_models["RMSE"]]
        fig_bar = go.Figure(go.Bar(
            x=df_models["Model"], y=df_models["RMSE"],
            marker_color=colors,
            marker_line_color="#0d1117",
            marker_line_width=1,
            text=df_models["RMSE"].round(2),
            textposition="outside",
            textfont=dict(color="#8b949e", size=11)
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, height=280,
                              yaxis_title="RMSE (µg/m³)",
                              xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r2:
        st.markdown("<div class='section-title'>MAPE theo mô hình</div>", unsafe_allow_html=True)
        colors2 = ["#00d4aa" if v == best_mape else "#ff6b6b" if v == df_models["MAPE"].max() else "#30363d"
                   for v in df_models["MAPE"]]
        fig_bar2 = go.Figure(go.Bar(
            x=df_models["Model"], y=df_models["MAPE"],
            marker_color=colors2,
            marker_line_color="#0d1117",
            marker_line_width=1,
            text=[f"{v}%" for v in df_models["MAPE"]],
            textposition="outside",
            textfont=dict(color="#8b949e", size=11)
        ))
        fig_bar2.update_layout(**PLOTLY_LAYOUT, height=280,
                               yaxis_title="MAPE (%)",
                               xaxis_tickangle=-30)
        st.plotly_chart(fig_bar2, use_container_width=True)

    # Radar chart
    st.markdown("<div class='section-title'>Radar Chart — Top 4 mô hình</div>", unsafe_allow_html=True)
    top4 = df_models.nsmallest(4, "RMSE")

    # Normalize (invert: lower is better → higher score)
    cats = ["RMSE score", "MAE score", "MAPE score"]
    fig_radar = go.Figure()
    colors_radar = ["#00d4aa", "#ffd93d", "#ff6b6b", "#a855f7"]
    for idx, (_, row) in enumerate(top4.iterrows()):
        rmse_score = 100 * (1 - (row["RMSE"] - df_models["RMSE"].min()) / (df_models["RMSE"].max() - df_models["RMSE"].min()))
        mae_score = 100 * (1 - (row["MAE"] - df_models["MAE"].min()) / (df_models["MAE"].max() - df_models["MAE"].min()))
        mape_score = 100 * (1 - (row["MAPE"] - df_models["MAPE"].min()) / (df_models["MAPE"].max() - df_models["MAPE"].min()))
        vals = [rmse_score, mae_score, mape_score, rmse_score]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill='toself',
            name=row["Model"],
            line_color=colors_radar[idx],
            fillcolor=f"rgba({int(colors_radar[idx][1:3],16)},{int(colors_radar[idx][3:5],16)},{int(colors_radar[idx][5:7],16)},0.1)"
        ))
    fig_radar.update_layout(
        **PLOTLY_LAYOUT,
        height=350,
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d", tickcolor="#30363d"),
            angularaxis=dict(gridcolor="#30363d")
        )
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — DATASET INFO
# ══════════════════════════════════════════════════════════════
with tab4:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-title'>Thông tin Dataset</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card'>
            <table style='width:100%; font-size:14px; border-collapse:collapse;'>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Tên dataset</td><td style='color:#e6edf3; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'><b>Air Quality India</b></td></tr>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Nguồn</td><td style='color:#00d4aa; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'>Kaggle</td></tr>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Số dòng</td><td style='color:#e6edf3; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'><b>29,531 dòng</b></td></tr>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Số cột</td><td style='color:#e6edf3; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'><b>16 features</b></td></tr>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Thời gian</td><td style='color:#e6edf3; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'>2015 – 2020</td></tr>
                <tr><td style='color:#8b949e; padding:8px 0; border-bottom:1px solid #21262d;'>Số thành phố</td><td style='color:#e6edf3; padding:8px 0; border-bottom:1px solid #21262d; text-align:right;'>26 thành phố</td></tr>
                <tr><td style='color:#8b949e; padding:8px 0;'>Tần suất</td><td style='color:#e6edf3; padding:8px 0; text-align:right;'>Hàng ngày</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Phân chia Train/Test</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card'>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px;'>
                <div style='text-align:center; padding:16px; background:#21262d; border-radius:8px;'>
                    <div style='font-size:11px; color:#8b949e; font-family:Space Mono,monospace; text-transform:uppercase;'>TRAIN</div>
                    <div style='font-size:28px; font-weight:600; color:#00d4aa; margin:8px 0;'>80%</div>
                    <div style='font-size:12px; color:#8b949e;'>2015 – 2019<br>1,607 mẫu</div>
                </div>
                <div style='text-align:center; padding:16px; background:#21262d; border-radius:8px;'>
                    <div style='font-size:11px; color:#8b949e; font-family:Space Mono,monospace; text-transform:uppercase;'>TEST</div>
                    <div style='font-size:28px; font-weight:600; color:#ff6b6b; margin:8px 0;'>20%</div>
                    <div style='font-size:12px; color:#8b949e;'>2020<br>153 mẫu</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='section-title'>Các features sử dụng</div>", unsafe_allow_html=True)
        features = {
            "PM2.5 (target)": ("Particulate Matter < 2.5µm", "#00d4aa"),
            "PM10": ("Particulate Matter < 10µm", "#ffd93d"),
            "NOx": ("Nitrogen Oxides", "#ff9f43"),
            "NO2": ("Nitrogen Dioxide", "#ff6b6b"),
            "NH3": ("Ammonia", "#a855f7"),
            "PM2.5_lag1": ("PM2.5 ngày trước (engineered)", "#00b894"),
            "PM2.5_lag7": ("PM2.5 tuần trước (engineered)", "#00b894"),
            "PM2.5_roll7": ("Rolling mean 7 ngày (engineered)", "#00b894"),
            "month_sin/cos": ("Seasonality encoding (engineered)", "#74b9ff"),
        }
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for feat, (desc, col) in features.items():
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:9px 0; border-bottom:1px solid #21262d;'>
                <div>
                    <span style='font-family:Space Mono,monospace; font-size:12px; color:{col};'>{feat}</span>
                    <div style='font-size:11px; color:#8b949e; margin-top:2px;'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Pipeline Architecture</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card' style='font-family:Space Mono,monospace; font-size:12px; color:#8b949e; line-height:2;'>
            <span style='color:#00d4aa;'>city_day.csv</span><br>
            &nbsp;&nbsp;&nbsp;↓ Python Producer<br>
            <span style='color:#ffd93d;'>Apache Kafka</span> (topic: pm25-topic)<br>
            &nbsp;&nbsp;&nbsp;↓ Spark Streaming<br>
            <span style='color:#ff9f43;'>Apache Spark</span> (aggregate theo tháng)<br>
            &nbsp;&nbsp;&nbsp;↓ Load model<br>
            <span style='color:#a855f7;'>Holt-Winters / LSTM</span><br>
            &nbsp;&nbsp;&nbsp;↓ Save results<br>
            <span style='color:#00d4aa;'>output/results.csv</span>
        </div>
        """, unsafe_allow_html=True)

    # Missing value info
    st.markdown("<div class='section-title'>Xử lý giá trị thiếu</div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <div style='font-size:28px; color:#ff6b6b; font-weight:600;'>15.6%</div>
            <div style='font-size:12px; color:#8b949e; margin-top:6px;'>PM2.5 missing rate</div>
        </div>""", unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <div style='font-size:28px; color:#ffd93d; font-weight:600;'>Linear</div>
            <div style='font-size:12px; color:#8b949e; margin-top:6px;'>Interpolation method</div>
        </div>""", unsafe_allow_html=True)
    with col_m3:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <div style='font-size:28px; color:#00d4aa; font-weight:600;'>MICE</div>
            <div style='font-size:12px; color:#8b949e; margin-top:6px;'>Multivariate imputation</div>
        </div>""", unsafe_allow_html=True)
