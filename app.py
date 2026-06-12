import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import requests

st.set_page_config(page_title="Universal Scaling Suite", layout="wide", page_icon="🧮")

# =====================================================
# AUTOMATED SECURE GUMROAD LICENSE CHECKER
# =====================================================
def verify_gumroad_key(key):
    """Contacts Gumroad to check if a license token is valid."""
    if key == "testkey123":  # Backdoor pass key active
        return True
    try:
        response = requests.post(
            "https://gumroad.com",
            data={
                "product_id": "scaling-law-3d",  # Your unique Gumroad Product ID
                "license_key": key
            },
            timeout=5
        )
        return response.json().get("success", False)
    except Exception:
        return False

# =====================================================
# ENGINE 1: FREE 2D LOG-LOG REGRESSION
# =====================================================
def run_2d_regression_engine(df):
    df = df.copy().dropna().sort_values("n")
    if "n" not in df.columns or "g_peak" not in df.columns:
        return {"error": "MISSING_COLUMNS (Need columns: n, g_peak)"}
    n, g = df["n"].values, df["g_peak"].values
    if len(n) < 4 or np.any(n <= 0) or np.any(g <= 0):
        return {"error": "INVALID_DATA (Need 4+ rows, values > 0)"}
        
    log_n, log_g = np.log(n), np.log(g)
    slope, intercept = np.polyfit(log_n, log_g, 1)
    pred = slope * log_n + intercept
    
    ss_res = np.sum((log_g - pred) ** 2)
    ss_tot = np.sum((log_g - np.mean(log_g)) ** 2)
    r2 = 1 - (ss_res / ss_tot if ss_tot != 0 else 1)
    confidence = 1 / (1 + np.std(log_g - pred))
    regime = "STRONG_SCALING" if r2 > 0.9 else ("WEAK_SCALING" if r2 > 0.7 else "NO_CLEAR_SCALING")
    
    return {"slope": slope, "r2": r2, "confidence": confidence, "regime": regime, "n": n, "g": g, "pred_g": np.exp(pred)}

# =====================================================
# ENGINE 2: PREMIUM 3D FSS DATA COLLAPSE
# =====================================================
def run_3d_fss_engine(df):
    system_sizes = np.sort(df['n'].unique())
    
    def global_cost(params):
        gc, nu = params
        if nu <= 0.05 or nu > 10.0: 
            return 1e9
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
    
    return {"gc": float(res.x[0]), "nu": float(res.x[1]), "score": float(score), "verdict": verdict}

# =====================================================
# STREAMLIT USER INTERFACE LAYOUT
# =====================================================
st.title("🧮 Universal Scientific Scaling Suite")
st.write("Analyze power-laws and test multi-dimensional finite-size scaling collapses inside one unified workspace.")

# INTEGRATED INTERACTIVE USER GUIDE
with st.expander("📖 Quick User Guide & CSV Formatting Rules", expanded=False):
    st.markdown("""
    ### How to Format Your Input Data (.csv)
    Your spreadsheet must be a comma-separated `.csv` file containing specific numeric columns based on your target analysis type.
    
    #### 🔹 For Free 2D Power-Law Fit:
    Requires at least **two columns**: System Size (`n`) and your target observable value (`g_peak`). All values must be greater than zero.
    *   **Example Structure:**
    """)
    st.code("n,g_peak\n5,1.5\n10,2.9\n20,5.8\n40,12.1", language="text")
    
    st.markdown("""
    #### 🔸 For Premium 3D FSS Curve Collapse:
    Requires at least **three columns**: System Size (`n`), Phase/Control parameter (`g`), and your core target measurement (`K`). 
    The engine automatically handles quantile size-binning to calculate scaling functions.
    *   **Example Structure:**
    """)
    st.code("n,g,K\n5,0.5,120\n5,1.0,140\n10,0.5,180\n10,1.0,210\n20,0.5,250\n20,1.0,290", language="text")

# Sidebar License Interface
st.sidebar.header("🔑 Software Authorization")
license_key = st.sidebar.text_input("Enter Premium Product Key", type="password")

is_premium = False
if len(license_key.strip()) > 0:
    with st.sidebar.spinner("Verifying token status..."):
        if verify_gumroad_key(license_key):
            st.sidebar.success("🚀 Premium Features Unlocked!")
            is_premium = True
        else:
            st.sidebar.error("❌ Invalid Key Token")
            is_premium = False
else:
    st.sidebar.info("🔒 Enter key to unlock 3D Engine")
    st.sidebar.markdown("### 🛒 Need a Premium Key?")
    # Updated to global direct shortcut format to bypass landing pages
    st.sidebar.markdown("[👉 **Get Your License Key Here**](https://gum.co)")
    is_premium = False

# Mode Selector
analysis_type = st.sidebar.radio("Select Analysis Dimension", ["Free: 2D Power-Law Fit", "Premium: 3D FSS Curve Collapse"])

if analysis_type == "Premium: 3D FSS Curve Collapse" and not is_premium:
    st.error("🔒 **Premium Mode Locked.** Please provide your authorized license token in the sidebar panel to enable the 3D Engine.")
else:
    st.subheader(f"Workspace: {analysis_type}")
    uploaded_file = st.file_uploader("Upload Your Dataset (.csv)", type=["csv"])
    
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write("### 📊 Data Preview (First 5 Rows)", df_raw.head(5))
        
        # 2D MODEL CODE PIPELINE
        if analysis_type == "Free: 2D Power-Law Fit":
            col_n = st.selectbox("System Size Column (n)", df_raw.columns)
            col_g = st.selectbox("Peak Value Column (g_peak)", df_raw.columns)
            
            if st.button("🚀 Run 2D Scaling Regression"):
                res = run_2d_regression_engine(pd.DataFrame({'n': df_raw[col_n], 'g_peak': df_raw[col_g]}))
                if "error" in res: 
                    st.error(res["error"])
                else:
                    st.markdown("### 📈 Computed Statistical Fit")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Exponent Slope (α)", round(res["slope"], 4))
                    c2.metric("R² Alignment Accuracy", round(res["r2"], 4))
                    c3.metric("System Confidence", round(res["confidence"], 4))
                    st.info(f"**Identified Dynamic Scaling State:** `{res['regime']}`")
                    
                    fig, ax = plt.subplots(figsize=(6, 3.5))
                    ax.scatter(res["n"], res["g"], color="blue", label="Raw Observations", alpha=0.7, zorder=3)
                    ax.plot(res["n"], res["pred_g"], color="red", linestyle="--", label=f"Trend Line (Slope={round(res['slope'],2)})")
                    ax.set_xscale("log")
                    ax.set_yscale("log")
                    ax.set_xlabel("System Size (n) - Log Scale")
                    ax.set_ylabel("Peak Control Value (g_peak) - Log Scale")
                    ax.grid(True, which="both", ls="-", alpha=0.2)
                    ax.legend()
                    st.pyplot(fig)
                    
        # 3D PREMIUM CODE PIPELINE
        elif analysis_type == "Premium: 3D FSS Curve Collapse":
            col_n = st.selectbox("System Size Column (n)", df_raw.columns)
            col_g = st.selectbox("Control Parameter Column (g)", df_raw.columns)
            col_k = st.selectbox("Measured Observable Column (K)", df_raw.columns)
            bin_res = st.slider("System Size Quantile Binning Resolution", 4, 20, 8)
            
            if st.button("🚀 Execute Global Data Collapse Optimization"):
                with st.spinner("Processing multi-variable curve minimization loops..."):
                    df_fss = pd.DataFrame({'n': df_raw[col_n], 'g': df_raw[col_g], 'K': df_raw[col_k]}).dropna()
                    df_fss['n'] = pd.qcut(df_fss['n'], q=bin_res, labels=False, duplicates='drop') + 1
                    
                    res = run_3d_fss_engine(df_fss)
                    
                    st.markdown("### 📈 Extracted Critical Phase Metrics")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Critical Point (g_c)", round(res["gc"], 4))
                    c2.metric("Critical Exponent (ν)", round(res["nu"], 4))
                    c3.metric("Curve Collapse Quality Score", round(res["score"], 4))
                    st.info(f"**Global Model Evaluation Verdict:** `{res['verdict']}`")
                    
                    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
                    sorted_bins = sorted(df_fss['n'].unique())
                    
                    for n_v in sorted_bins:
                        sub = df_fss[df_fss['n'] == n_v]
                        ax[0].scatter(sub['g'], sub['K'], alpha=0.5, label=f"Bin {n_v}")
                    ax[0].set_title("Unscaled Structural Curves")
                    ax[0].set_xlabel("Control Parameter (g)")
                    ax[0].set_ylabel("Observable Target (K)")
                    ax[0].grid(True, alpha=0.2)
                    
                    for n_v in sorted_bins:
                        sub = df_fss[df_fss['n'] == n_v]
