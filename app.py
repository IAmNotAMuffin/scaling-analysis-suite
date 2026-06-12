import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

st.set_page_config(page_title="Premium FSS Engine", layout="wide", page_icon="🧮", initial_sidebar_state="expanded")

# ==========================================
# PREMIUM 3D FSS DATA COLLAPSE ENGINE
# ==========================================
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
    
    # Securely map array indices to distinct dictionary floats
    return {"gc": float(res.x[0]), "nu": float(res.x[1]), "score": float(score), "verdict": verdict}

# ==========================================
# STREAMLIT USER INTERFACE LAYOUT
# ==========================================
st.title("🧮 Premium 3D Finite-Size Scaling Suite")
st.write("Perform multi-dimensional curve optimizations and universal data scaling calculations instantly.")

# Sidebar verification logic flow
st.sidebar.header("🔑 Software Authorization")
license_key = st.sidebar.text_input("Enter Premium Product Key", type="password")

if license_key == "testkey123":
    st.sidebar.success("🚀 Premium Features Unlocked!")
    is_premium = True
elif len(license_key.strip()) > 0:
    st.sidebar.error("❌ Invalid Key Token")
    is_premium = False
else:
    st.sidebar.info("🔒 Enter key to unlock 3D Engine")
    st.sidebar.markdown("### 🛒 Storefront Page")
    st.sidebar.markdown("[👉 Click Here to Get a Key](https://gumroad.com)")
    is_premium = False

# Content Wrapper Block
if not is_premium:
    st.warning("⚠️ Please provide a valid product authorization key token in the sidebar panel to enable data imports.")
else:
    uploaded_file = st.file_uploader("Upload Structural Research File (.csv)", type=["csv"])

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write("### Data Preview", df_raw.head(5))
        
        st.info("Map your multi-variable parameters to engine data inputs:")
        col_n = st.selectbox("System Size Variable (n)", df_raw.columns)
        col_g = st.selectbox("Control Parameter (g)", df_raw.columns)
        col_k = st.selectbox("Measured Observable (K)", df_raw.columns)
        bin_res = st.slider("Scaling Resolution Binning Count", 5, 20, 8)
        
        if st.button("🚀 Run Global Optimization Loop"):
            with st.spinner("Processing curves..."):
                df_fss = pd.DataFrame({'n': df_raw[col_n], 'g': df_raw[col_g], 'K': df_raw[col_k]}).dropna()
                df_fss['n'] = pd.qcut(df_fss['n'], q=bin_res, labels=False, duplicates='drop') + 1
                
                res = run_3d_fss_engine(df_fss)
                
                st.subheader("📈 Extracted Parameters")
                c1, c2, c3 = st.columns(3)
                c1.metric("Critical Point (g_c)", round(res["gc"], 4))
                c2.metric("Critical Exponent (ν)", round(res["nu"], 4))
                c3.metric("Collapse Quality Score", round(res["score"], 4))
                st.info(f"**Engine Evaluation:** `{res['verdict']}`")
                
                # Diagnostic plotting layout
                st.subheader("📊 Universal Curve Visualizations")
                fig, ax = plt.subplots(1, 2, figsize=(11, 4))
                
                for n_v in sorted(df_fss['n'].unique()):
                    sub = df_fss[df_fss['n'] == n_v]
                    ax.scatter(sub['g'], sub['K'], alpha=0.5, label=f"Bin {n_v}")
                ax.set_title("Unscaled Input Data")
                ax.set_xlabel("g")
                ax.set_ylabel("K")
                ax.grid(True, alpha=0.2)
                
                for n_v in sorted(df_fss['n'].unique()):
                    sub = df_fss[df_fss['n'] == n_v]
                    x_collapsed = (sub['g'] - res["gc"]) * (n_v ** (1 / res["nu"]))
                    ax.scatter(x_collapsed, sub['K'], alpha=0.5)
                ax.set_title("Optimized Data Collapse")
                ax.set_xlabel(f"(g - {round(res['gc'],2)}) * n^(1/{round(res['nu'],2)})")
                ax.grid(True, alpha=0.2)
                
                st.pyplot(fig)
