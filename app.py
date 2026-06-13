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
    """Contacts Gumroad API endpoints to verify license validity."""
    try:
        response = requests.post(
            "https://gumroad.com",
            data={
                "product_id": "scaling-law-3d",
                "license_key": key
            },
            timeout=5
        )
        return response.json().get("success", False)
    except Exception:
        return False

# =====================================================
# ENGINE 1: 2D POWER-LAW REGRESSION
# =====================================================
def run_2d_regression_engine(df):
    df = df.copy().dropna().sort_values("n")
    if "n" not in df.columns or "g_peak" not in df.columns:
        return {"error": "MISSING_COLUMNS"}
        
    n = df["n"].values
    g = df["g_peak"].values
    
    if len(n) < 4 or np.any(n <= 0) or np.any(g <= 0):
        return {"error": "INVALID_DATA"}
        
    log_n = np.log(n)
    log_g = np.log(g)
    
    slope, intercept = np.polyfit(log_n, log_g, 1)
    pred = slope * log_n + intercept
    
    ss_res = np.sum((log_g - pred) ** 2)
    ss_tot = np.sum((log_g - np.mean(log_g)) ** 2)
    r2 = 1 - (ss_res / ss_tot if ss_tot != 0 else 1)
    confidence = 1 / (1 + np.std(log_g - pred))
    
    regime = "STRONG_SCALING" if r2 > 0.9 else ("WEAK_SCALING" if r2 > 0.7 else "NO_CLEAR_SCALING")
    
    return {
        "slope": slope, 
        "r2": r2, 
        "confidence": confidence, 
        "regime": regime, 
        "n": n, 
        "g": g, 
        "pred_g": np.exp(pred)
    }

# =====================================================
# ENGINE 2: 3D FINITE SIZE SCALING COLLAPSE
# =====================================================
def run_3d_fss_engine(df):
    system_sizes = np.sort(df["n"].unique())
    
    def global_cost(params):
        gc, nu = params
        if nu <= 0.05 or nu > 10.0: 
            return 1e9
        variance = 0
        points = 0
        for n in system_sizes:
            sub = df[df["n"] == n]
            x_scaled = (sub["g"] - gc) * (n ** (1 / nu))
            y = sub["K"].values
            bins = np.linspace(x_scaled.min(), x_scaled.max(), 12)
            digit = np.digitize(x_scaled, bins)
            for i in range(1, len(bins)):
                vals = y[digit == i]
                if len(vals) > 2:
                    variance += (np.var(vals) * len(vals))
                    points += len(vals)
        return variance / max(points, 1)

    result = minimize(
        global_cost, 
        x0=[df["g"].mean(), 1.0], 
        bounds=[(df["g"].min(), df["g"].max()), (0.1, 5.0)], 
        method="L-BFGS-B"
    )
    score = 1 / (1 + result.fun)
    verdict = "STRONG UNIVERSAL SCALING" if score > 0.8 else ("WEAK SCALING" if score > 0.4 else "NO UNIVERSAL SCALING")
    
    return {
        "gc": float(result.x[0]), 
        "nu": float(result.x[1]), 
        "score": float(score), 
        "verdict": verdict
    }

# =====================================================
# STREAMLIT USER INTERFACE LAYOUT
# =====================================================
st.title("🧮 Universal Scientific Scaling Suite")
st.write("Analyze power laws and finite-size scaling collapse inside one unified scientific workspace.")

with st.expander("📖 CSV Formatting Rules"):
    st.code("n,g,K\n5,0.5,120\n5,1.0,140\n10,0.5,180", language="text")

# =====================================================
# LICENSE PANEL & STOREFRONT LINKS
# =====================================================
st.sidebar.header("🔑 Authorization")
license_key = st.sidebar.text_input("Premium Key", type="password")

is_premium = False
if license_key:
    with st.sidebar.spinner("Checking..."):
        if verify_gumroad_key(license_key):
            st.sidebar.success("Premium unlocked")
            is_premium = True
        else:
            st.sidebar.error("Invalid key")
else:
    st.sidebar.info("Premium locked")
    st.sidebar.markdown("### 🛒 Need a Premium Key?")
    st.sidebar.markdown("[👉 **Get Your License Key Here**](https://gumroad.com)")

analysis_type = st.sidebar.radio(
    "Analysis Mode", 
    ["Free: 2D Power-Law Fit", "Premium: 3D FSS Curve Collapse"]
)

# =====================================================
# DATA SOURCE INTEGRATION
# =====================================================
source = st.selectbox(
    "Dataset Source", 
    ["Upload Custom CSV File", "Model Example: Ising FSS", "Model Example: NASA Kepler"]
)

df_raw = None
if source == "Upload Custom CSV File":
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file:
        df_raw = pd.read_csv(file)
elif source == "Model Example: Ising FSS":
    ns = [4, 8, 16, 32]
    rows = []
    for n in ns:
        for t in np.linspace(2, 2.5, 20):
            rows.append({
                "n": n, 
                "g": t, 
                "K": 1 / (1 + np.exp((t - 2.2691) * n))
            })
    df_raw = pd.DataFrame(rows)
elif source == "Model Example: NASA Kepler":
    ns = [10, 20, 40, 80, 160]
    df_raw = pd.DataFrame({
        "n": ns, 
        "g_peak": [5000 / (x ** 0.85) for x in ns]
    })

# =====================================================
# ENGINE OPERATIONS INTERFACES
# =====================================================
if analysis_type == "Premium: 3D FSS Curve Collapse" and not is_premium:
    st.error("Premium feature locked. Please provide your authorized license token in the sidebar panel.")
elif df_raw is not None:
    st.write("### Active Dataset Preview", df_raw.head())
    
    if analysis_type == "Free: 2D Power-Law Fit":
        n_col = st.selectbox("Select n column", df_raw.columns)
        g_col = st.selectbox("Select g_peak column", df_raw.columns)
        
        if st.button("🚀 Run Regression"):
            # Packaging parameters cleanly explicitly maps user variables to engine fields
            input_df = pd.DataFrame({
                "n": df_raw[n_col], 
                "g_peak": df_raw[g_col]
            })
            result = run_2d_regression_engine(input_df)
            
            if "error" in result:
                st.error(f"Execution Error: {result['error']}")
            else:
                st.markdown("### Fit Metrics")
                c1, c2, c3 = st.columns(3)
                c1.metric("Exponent", round(result["slope"], 5))
                c2.metric("R² Alignment Accuracy", round(res["r2"], 4) if 'res' in locals() else round(result["r2"], 5))
                c3.metric("Confidence", round(result["confidence"], 5))
                st.info(f"Dynamic Regime: `{result['regime']}`")
                
                fig, ax = plt.subplots(figsize=(6, 3.5))
                ax.scatter(result["n"], result["g"], color="blue", alpha=0.7)
                ax.plot(result["n"], result["pred_g"], color="red", linestyle="--")
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.set_xlabel("n (Log Scale)")
                ax.set_ylabel("g_peak (Log Scale)")
                ax.grid(True, which="both", alpha=0.2)
                st.pyplot(fig)
                
    elif analysis_type == "Premium: 3D FSS Curve Collapse":
        n_col = st.selectbox("Select n column", df_raw.columns)
        g_col = st.selectbox("Select g column", df_raw.columns)
        k_col = st.selectbox("Select K column", df_raw.columns)
        
        if st.button("🚀 Run 3D Collapse"):
            input_df = pd.DataFrame({
                "n": df_raw[n_col], 
                "g": df_raw[g_col], 
                "K": df_raw[k_col]
            })
            result = run_3d_fss_engine(input_df)
            
            st.markdown("### Collapse Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Critical Point", round(result["gc"], 5))
            c2.metric("Exponent ν", round(result["nu"], 5))
            c3.metric("Collapse Score", round(result["score"], 5))
            st.success(result["verdict"])
            
            fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
            sorted_bins = sorted(input_df["n"].unique())
            
            for n_v in sorted_bins:
                sub = input_df[input_df["n"] == n_v]
                ax[0].scatter(sub["g"], sub["K"], alpha=0.6, label=f"n={n_v}")
            ax[0].set_title("Unscaled Curves")
            ax[0].grid(True, alpha=0.2)
            
            for n_v in sorted_bins:
                sub = input_df[input_df["n"] == n_v]
                x_collapsed = (sub["g"] - result["gc"]) * (n_v ** (1 / result["nu"]))
                ax[1].scatter(x_collapsed, sub["K"], alpha=0.6)
            ax[1].set_title("Optimized Data Collapse")
            ax[1].grid(True, alpha=0.2)
            st.pyplot(fig)
