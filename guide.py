# =====================================================
# INDEPENDENT HEAVY TEXT VAULT (PREVENTS WINDOW OVERFLOW)
# =====================================================

RULES_2D = """
### How to Format Your Input Data (.csv)
Your spreadsheet must be a comma-separated `.csv` file containing specific numeric columns based on your target analysis type.

#### 🔹 For Free 2D Power-Law Fit:
Requires at least **two columns**: System Size (`n`) and your target observable value (`g_peak`). All values must be greater than zero.
*   **Example Structure:**
"""

RULES_3D = """
#### 🔸 For Premium 3D FSS Curve Collapse:
Requires at least **three columns**: System Size (`n`), Phase/Control parameter (`g`), and your core target measurement (`K`). 
The engine automatically handles quantile size-binning to calculate scaling functions.
*   **Example Structure:**
"""
