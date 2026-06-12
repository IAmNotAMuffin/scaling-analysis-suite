import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

st.set_page_config(page_title="Universal Scaling Suite", layout="wide", page_icon="🧮")

# ==========================================
# ENGINE 1: FREE 2D LOG-LOG REGRESSION
# ==========================================
def run_2d_regression_engine(df):
    df = df.copy().dropna().sort_values("n")
    if "n" not in df.columns or "g_peak" not in df.columns:
        return {"error": "MISSING_COLUMNS (Need columns: n, g_peak)"}
    n, g = df["n"].values, df["g_peak"].values
    if len(n) < 4 or np.any(n <= 0) or np.any(g <= 0):
        return {"error": "INVALID_OR_INSUFFICIENT_DATA (Need 4+ rows, values > 0)"}
        
    log_n, log_g = np.log(n), np.log(g)
    slope, intercept = np.polyfit(log_n, log_g, 1)
    pred = slope * log_n + intercept
    
    r2 = 1 - (np.sum((log_g - pred) ** 2) / np.sum((log_g - np.mean(log_g)) ** 2) if np.sum((log_g - np.mean(log_g)) ** 2) != 0 else 1)
    confidence = 1 / (1 + np.std(log_g - pred))
    regime = "STRONG_SCALING" if r2 > 0.9 else ("WEAK_SCALING" if r2 > 0.7 else "NO_CLEAR_SCALING")
    
    return {"slope": slope, "r2": r2, "confidence": confidence, "regime": regime, "n": n, "g": g, "pred_g": np.exp(pred)}

# ==========================================
# ENGINE 2: PREMIUM 3D FSS DATA COLLAPSE
# ==========================================
def run_3d_fss_engine(df):
    system_sizes = np.sort(df['n'].unique())
    
    def global_cost(params):
        gc, nu = params
        if nu <= 0.05 or nu > 10.0: return 1e9
        total_variance, total_points = 0, 0
        for n in system_sizes:
            sub = df[df['n'] == n]
            x_scaled = (sub['g'] - gc) * (n ** (1 / nu))
            y_values = sub['K'].values
            bins = np.linspace(np.min(x_scaled), np.max(x_scaled), 12)
            digit = np.digitize(x_scaled, bins)
            for i in range(1, len(bins)):
                points_in_bin = y_values[digit == i]
                if len(points_in_bin) > 2:
                    total_variance += np.var(points_in_bin) * len(points_in_bin)
                    total_points += len(points_in_bin)
        return total_variance / max(total_points, 1)

    res = minimize(global_cost, x0=[df['g'].mean(), 1.0], bounds=[(df['g'].min(), df['g'].max()), (0.1, 5.0)], method='L-BFGS-B')
    score = 1.0 / (1.0 + res.fun)
    verdict = "STRONG UNIVERSAL SCALING" if score > 0.8 else ("WEAK SCALING" if score > 0.4 else "NO UNIVERSAL SCALING")
    return {"gc": res.x[0], "nu": res.x[1], "score": score, "verdict": verdict}

# ==========================================
# STREAMLIT USER INTERFACE
# ==========================================
st.title("🧮 Universal Scientific Scaling Suite")
st.write("Analyze power-laws and test multi-dimensional finite-size scaling collapses inside one unified workspace.")

# Sidebar License wall
st.sidebar.header("🔑 Software Authorization")
license_key = st.sidebar.text_input("Enter Premium Product Key", type="password")
is_premium = len(license_key.strip()) > 0

analysis_type = st.sidebar.radio("Select Analysis Dimension", ["Free: 2D Power-Law Fit", "Premium: 3D FSS Curve Collapse"])

if analysis_type == "Premium: 3D FSS Curve Collapse" and not is_premium:
    st.error("🔒 **Premium Mode Locked.** Enter a product key in the sidebar to unlock 3D Finite-Size Scaling analysis.")
    st.info("💡 Researchers use the Premium mode to perform data collapse algorithms using multi-variable datasets.")
else:
    st.subheader(f"Workspace: {analysis_type}")
    uploaded_file = st.file_uploader("Upload Data File (.csv)", type=["csv"])
    
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write("### Data Preview", df_raw.head(5))
        
        if analysis_type == "Free: 2D Power-Law Fit":
            col_n = st.selectbox("System Size Variable (n)", df_raw.columns)
            col_g = st.selectbox("Peak Value Variable (g_peak)", df_raw.columns)
            
            if st.button("🚀 Run 2D Analysis"):
                res = run_2d_regression_engine(pd.DataFrame({'n': df_raw[col_n], 'g_peak': df_raw[col_g]}))
                if "error" in res: st.error(res["error"])
                else:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Scaling Exponent (Slope)", round(res["slope"], 4))
                    c2.metric("R² Fit Quality", round(res["r2"], 4))
                    c3.metric("Confidence Score", round(res["confidence"], 4))
                    st.success(f"**Regime Status:** {res['regime']}")
                    
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.scatter(res["n"], res["g"], color="blue", label="Data")
                    ax.plot(res["n"], res["pred_g"], color="red", linestyle="--", label="Fit Line")
                    ax.set_xscale("log"); ax.set_yscale("log")
                    ax.set_xlabel("n (Log)"); ax.set_ylabel("g_peak (Log)"); ax.legend(); ax.grid(True)
                    st.pyplot(fig)
                    
        elif analysis_type == "Premium: 3D FSS Curve Collapse":
            col_n = st.selectbox("System Size Variable (n)", df_raw.columns)
            col_g = st.selectbox("Control Parameter (g)", df_raw.columns)
            col_k = st.selectbox("Measured Observable (K)", df_raw.columns)
            bin_res = st.slider("Scaling Resolution Binning Count", 5, 20, 8)
            
            if st.button("🚀 Run Premium 3D Data Collapse"):
                df_fss = pd.DataFrame({'n': df_raw[col_n], 'g': df_raw[col_g], 'K': df_raw[col_k]}).dropna()
                df_fss['n'] = pd.qcut(df_fss['n'], q=bin_res, labels=False, duplicates='drop') + 1
                
                res = run_3d_fss_engine(df_fss)
                c1, c2, c3 = st.columns(3)
                c1.metric("Critical Transition Point (g_c)", round(res["gc"], 4))
                c2.metric("Critical Exponent (ν)", round(res["nu"], 4))
                c3.metric("Curve Collapse Quality", round(res["score"], 4))
                st.info(f"**Verdict:** {res['verdict']}")
                
                fig, ax = plt.subplots(1, 2, figsize=(10, 4))
                for n_v in sorted(df_fss['n'].unique()):
                    sub = df_fss[df_fss['n'] == n_v]
                    ax[0].scatter(sub['g'], sub['K'], alpha=0.5, label=f"Bin {n_v}")
                    ax[1].scatter((sub['g'] - res["gc"]) * (n_v ** (1 / res["nu"])), sub['K'], alpha=0.5)
                ax[0].set_title("Unscaled Curves"); ax[1].set_title("Optimized Data Collapse")
                ax[0].grid(True); ax[1].grid(True)
                st.pyplot(fig)
