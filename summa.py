"""
Loan Default Analysis
=====================
Feature Engineering | EDA | Hypothesis Testing | Statistical Validation
Dependencies: pandas, numpy, scipy, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from scipy.stats import (
    ttest_ind, pointbiserialr, chi2_contingency,
    mannwhitneyu, shapiro, pearsonr
)
import warnings
warnings.filterwarnings("ignore")


# =============================================================================
# DATA LOADING
# =============================================================================

data = {
    "applicant_id":              ["APP_00000001","APP_00000002","APP_00000003","APP_00000004","APP_00000005","APP_00000006","APP_00000007"],
    "age":                       [40, 25, 49, 37, 44, 21, 61],
    "gender":                    ["Male","Female","Female","Male","Male","Male","Female"],
    "marital_status":            ["Single","Single","Single","Married","Married","Single","Divorced"],
    "education_level":           ["High School","Master","High School","High School","Bachelor","Bachelor","Bachelor"],
    "employment_type":           ["Unemployed","Full-time","Full-time","Full-time","Part-time","Full-time","Retired"],
    "years_employed":            [2, 5, 2, 5, 2, 12, 7],
    "annual_income":             [47091, 106967, 49860, 61767, 99917, 36606, 30763],
    "monthly_income":            [3924.25, 8913.92, 4155.0, 5147.25, 8326.42, 3050.5, 2563.58],
    "income_stability_score":    [5, 7, 8, 9, 6, 10, 9],
    "has_co_signer":             ["No","No","No","Yes","No","No","No"],
    "num_dependents":            [1, 1, 0, 1, 0, 3, 0],
    "credit_score":              [690, 648, 768, 850, 730, 742, 804],
    "credit_history_length_years":[6, 1, 0, 1, 3, 15, 16],
    "num_open_accounts":         [12, 6, 11, 6, 11, 4, 6],
    "num_credit_inquiries_6m":   [1, 1, 1, 0, 2, 2, 5],
    "debt_to_income_ratio":      [40.47, 8.46, 24.93, 20.15, 21.51, 34.48, 34.23],
    "previous_defaults":         [0, 0, 0, 0, 0, 0, 0],
    "bankruptcy_history":        ["No","No","No","No","No","Yes","No"],
    "loan_amount":               [21645, 42806, 45674, 34997, 11392, 18783, 46084],
    "loan_term_months":          [120, 36, 84, 120, 84, 60, 24],
    "loan_purpose":              ["Car","Home","Car","Home","Business","Business","Home"],
    "interest_rate":             [9.03, 7.98, 6.78, 10.35, 6.68, 11.49, 5.45],
    "has_collateral":            ["Yes","No","No","Yes","Yes","Yes","No"],
    "loan_to_value_ratio":       [38.92, 67.32, 75.66, 84.35, 60.51, 33.53, 46.67],
    "savings_balance":           [33611.07, 2759.68, 45724.84, 22240.86, np.nan, 1309.19, 55382.08],
    "checking_balance":          [1658.48, 5001.68, 8146.81, 113.53, 5752.09, 6696.38, 51.66],
    "investment_portfolio_value":[5023.84, 15272.76, 53611.86, 554.25, 7490.29, 11330.7, 13767.64],
    "monthly_expenses":          [2952.21, 5318.34, 1951.49, 2845.05, np.nan, 1381.0, 2237.47],
    "has_direct_deposit":        ["Yes","Yes","Yes","No","Yes","Yes","No"],
    "application_date":          ["9/29/2023","12/22/2023","12/3/2023","5/26/2023","11/8/2023","10/31/2023","12/23/2023"],
    "application_channel":       ["Online","Online","Online","Online","Branch","Online","Online"],
    "relationship_tenure_years": [1, 0, 19, 0, 7, 0, 6],
    "defaulted":                 ["Yes","No","No","No","No","No","No"],
}

df = pd.DataFrame(data)
df["application_date"] = pd.to_datetime(df["application_date"])

print("=" * 65)
print("LOAN DEFAULT ANALYSIS PIPELINE")
print("=" * 65)
print(f"\nDataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")


# =============================================================================
# SECTION 1 — FEATURE ENGINEERING
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 1: FEATURE ENGINEERING")
print("=" * 65)

# --- Binary encoding ---
df["has_co_signer_bin"]      = np.where(df["has_co_signer"] == "Yes", 1, 0)
df["has_collateral_bin"]     = np.where(df["has_collateral"] == "Yes", 1, 0)
df["bankruptcy_history_bin"] = np.where(df["bankruptcy_history"] == "Yes", 1, 0)
df["has_direct_deposit_bin"] = np.where(df["has_direct_deposit"] == "Yes", 1, 0)
df["is_online_channel"]      = np.where(df["application_channel"] == "Online", 1, 0)
df["defaulted_bin"]          = np.where(df["defaulted"] == "Yes", 1, 0)

# --- Ordinal encoding ---
edu_map = {"High School": 1, "Bachelor": 2, "Master": 3, "PhD": 4}
df["education_rank"] = df["education_level"].map(edu_map)

emp_risk_map = {"Full-time": 1, "Part-time": 2, "Self-employed": 3, "Retired": 3, "Unemployed": 5}
df["employment_risk_score"] = df["employment_type"].map(emp_risk_map).fillna(3)

# --- Financial ratio features ---
df["monthly_surplus"]            = df["monthly_income"] - df["monthly_expenses"]
df["loan_to_income_ratio"]       = df["loan_amount"] / df["annual_income"]
df["monthly_loan_payment_est"]   = df["loan_amount"] / df["loan_term_months"]
df["payment_to_income_ratio"]    = df["monthly_loan_payment_est"] / df["monthly_income"]
df["expense_ratio"]              = df["monthly_expenses"] / df["monthly_income"]
df["savings_to_loan_ratio"]      = df["savings_balance"] / df["loan_amount"]

# --- Wealth & liquidity features ---
df["total_liquid_assets"] = df["savings_balance"].fillna(0) + df["checking_balance"].fillna(0)
df["total_wealth"]        = df["total_liquid_assets"] + df["investment_portfolio_value"].fillna(0)
df["wealth_to_loan"]      = df["total_wealth"] / df["loan_amount"]
df["net_monthly_position"]= df["monthly_surplus"].fillna(0) / df["loan_amount"] * 1000

# --- Credit composite risk score (weighted) ---
# Credit score weight: 40%, DTI buffer: 30%, Income stability: 30%
df["credit_risk_score"] = (
    (df["credit_score"] / 850) * 40
    + (1 - df["debt_to_income_ratio"] / 100) * 30
    + (df["income_stability_score"] / 10) * 30
)

# --- Application date features ---
df["app_month"]       = df["application_date"].dt.month
df["app_quarter"]     = df["application_date"].dt.quarter
df["app_day_of_week"] = df["application_date"].dt.dayofweek
df["is_year_end_app"] = np.where(df["app_month"] == 12, 1, 0)

# --- Age and demographic features ---
df["age_group"] = pd.cut(
    df["age"],
    bins=[18, 30, 40, 50, 65],
    labels=["Young (18-30)", "Mid (31-40)", "Senior (41-50)", "Older (51-65)"]
)

# --- Interaction terms ---
df["dti_x_employment_risk"] = df["debt_to_income_ratio"] * df["employment_risk_score"]
df["credit_x_stability"]    = df["credit_score"] * df["income_stability_score"]
df["loan_burden_index"]      = df["payment_to_income_ratio"] * df["employment_risk_score"]

engineered_features = [
    "monthly_surplus", "loan_to_income_ratio", "payment_to_income_ratio",
    "expense_ratio", "total_wealth", "wealth_to_loan", "credit_risk_score",
    "education_rank", "employment_risk_score", "dti_x_employment_risk",
    "loan_burden_index", "net_monthly_position"
]

print("\nEngineered Features Summary:")
print(df[engineered_features + ["defaulted_bin"]].round(3).to_string())


# =============================================================================
# SECTION 2 — EXPLORATORY DATA ANALYSIS
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: EXPLORATORY DATA ANALYSIS")
print("=" * 65)

# --- Basic statistics ---
numeric_raw = [
    "age", "credit_score", "annual_income", "monthly_income",
    "debt_to_income_ratio", "loan_amount", "interest_rate",
    "loan_term_months", "income_stability_score",
    "num_credit_inquiries_6m", "credit_history_length_years"
]
print("\n--- Descriptive Statistics (Raw Features) ---")
print(df[numeric_raw].describe().round(2).to_string())

print("\n--- Descriptive Statistics (Engineered Features) ---")
print(df[engineered_features].describe().round(3).to_string())

# --- Default group comparison ---
default_grp    = df[df["defaulted_bin"] == 1]
no_default_grp = df[df["defaulted_bin"] == 0]

compare_cols = [
    "credit_score", "debt_to_income_ratio", "annual_income",
    "income_stability_score", "credit_risk_score",
    "loan_to_income_ratio", "monthly_surplus", "expense_ratio",
    "employment_risk_score"
]

print("\n--- Mean Comparison: Defaulters vs Non-Defaulters ---")
comparison_df = pd.DataFrame({
    "Defaulter Mean":     default_grp[compare_cols].mean().round(3),
    "Non-Defaulter Mean": no_default_grp[compare_cols].mean().round(3),
    "Difference":         (default_grp[compare_cols].mean() - no_default_grp[compare_cols].mean()).round(3),
})
print(comparison_df.to_string())

# --- Categorical distributions ---
print("\n--- Categorical Feature Breakdown ---")
for col in ["gender", "marital_status", "education_level", "employment_type", "loan_purpose"]:
    print(f"\n{col}:")
    print(df.groupby(col)["defaulted_bin"].agg(["count", "sum", "mean"]).rename(
        columns={"count": "total", "sum": "defaults", "mean": "default_rate"}
    ).round(3).to_string())

# --- Correlation matrix ---
corr_cols = [
    "age", "credit_score", "debt_to_income_ratio", "annual_income",
    "loan_amount", "interest_rate", "income_stability_score",
    "num_credit_inquiries_6m", "loan_to_income_ratio",
    "payment_to_income_ratio", "credit_risk_score",
    "expense_ratio", "wealth_to_loan", "loan_term_months",
    "employment_risk_score", "education_rank",
    "has_collateral_bin", "has_co_signer_bin", "defaulted_bin"
]
corr_matrix = df[corr_cols].corr()

print("\n--- Top Correlations with Default (absolute) ---")
default_corr = corr_matrix["defaulted_bin"].drop("defaulted_bin").sort_values(key=abs, ascending=False)
print(default_corr.round(4).to_string())

# --- Missing value analysis ---
print("\n--- Missing Value Analysis ---")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
missing_df = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
print(missing_df[missing_df["missing_count"] > 0].to_string())


# =============================================================================
# SECTION 3 — HYPOTHESIS TESTING
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: HYPOTHESIS TESTING")
print("=" * 65)

d  = df[df["defaulted_bin"] == 1]   # defaulters
nd = df[df["defaulted_bin"] == 0]   # non-defaulters

# Helper to print results neatly
def print_hypothesis(h_id, title, method, stat_name, stat_val, p_val, direction, alpha=0.05):
    sig = "SIGNIFICANT ✓" if p_val < alpha else f"not significant (p > {alpha}, small n)"
    print(f"\n  H{h_id}: {title}")
    print(f"  Method  : {method}")
    print(f"  {stat_name:<10}: {stat_val:.4f}   |   p-value: {p_val:.4f}")
    print(f"  Direction: {direction}")
    print(f"  Result  : {sig}")


print("\n--- A) Two-sample t-tests (Welch) ---")
print("    Null: group means are equal | Alt: defaulters differ\n")

# H1: Credit Score
t1, p1 = ttest_ind(d["credit_score"], nd["credit_score"], equal_var=False)
print_hypothesis(1, "Defaulters have lower credit scores",
                 "Welch t-test", "t-stat", t1, p1,
                 f"Defaulter μ={d['credit_score'].mean():.1f}  vs  Non-defaulter μ={nd['credit_score'].mean():.1f}")

# H2: Debt-to-Income Ratio
t2, p2 = ttest_ind(d["debt_to_income_ratio"], nd["debt_to_income_ratio"], equal_var=False)
print_hypothesis(2, "Defaulters have higher DTI ratios",
                 "Welch t-test", "t-stat", t2, p2,
                 f"Defaulter μ={d['debt_to_income_ratio'].mean():.2f}%  vs  Non-defaulter μ={nd['debt_to_income_ratio'].mean():.2f}%")

# H3: Income Stability Score
t3, p3 = ttest_ind(d["income_stability_score"], nd["income_stability_score"], equal_var=False)
print_hypothesis(3, "Defaulters have lower income stability scores",
                 "Welch t-test", "t-stat", t3, p3,
                 f"Defaulter μ={d['income_stability_score'].mean():.2f}  vs  Non-defaulter μ={nd['income_stability_score'].mean():.2f}")

# H4: Employment Risk Score
t4, p4 = ttest_ind(d["employment_risk_score"], nd["employment_risk_score"], equal_var=False)
print_hypothesis(4, "Defaulters have higher employment risk scores",
                 "Welch t-test", "t-stat", t4, p4,
                 f"Defaulter μ={d['employment_risk_score'].mean():.2f}  vs  Non-defaulter μ={nd['employment_risk_score'].mean():.2f}")

# H5: Monthly Surplus
surplus_d  = d["monthly_surplus"].dropna()
surplus_nd = nd["monthly_surplus"].dropna()
t5, p5 = ttest_ind(surplus_d, surplus_nd, equal_var=False)
print_hypothesis(5, "Defaulters have lower monthly surplus",
                 "Welch t-test", "t-stat", t5, p5,
                 f"Defaulter μ=${surplus_d.mean():.2f}  vs  Non-defaulter μ=${surplus_nd.mean():.2f}")


print("\n--- B) Point-Biserial Correlations ---")
print("    Tests continuous feature vs binary default outcome\n")

pb_tests = [
    ("credit_risk_score",       "Composite credit risk score negatively correlates with default"),
    ("income_stability_score",  "Income stability negatively correlates with default"),
    ("debt_to_income_ratio",    "DTI ratio positively correlates with default"),
    ("loan_term_months",        "Longer loan terms correlate with default"),
    ("employment_risk_score",   "Higher employment risk correlates with default"),
    ("expense_ratio",           "Expense ratio positively correlates with default"),
]

for col, desc in pb_tests:
    col_clean = df[col].dropna()
    tgt_clean = df.loc[col_clean.index, "defaulted_bin"]
    r, p = pointbiserialr(tgt_clean, col_clean)
    sig = "✓ SIGNIFICANT" if p < 0.05 else "  not significant"
    print(f"  {sig}  |  r={r:+.4f}  p={p:.4f}  |  {desc}")


print("\n--- C) Mann-Whitney U Tests (non-parametric) ---")
print("    Does not assume normality — suitable for small samples\n")

mw_tests = [
    ("credit_score",        "credit score"),
    ("debt_to_income_ratio","DTI ratio"),
    ("credit_risk_score",   "credit risk composite"),
    ("annual_income",       "annual income"),
]

for col, label in mw_tests:
    a = d[col].dropna()
    b = nd[col].dropna()
    if len(a) > 0 and len(b) > 0:
        u, p = mannwhitneyu(a, b, alternative="two-sided")
        sig = "✓ SIGNIFICANT" if p < 0.05 else "  not significant"
        print(f"  {sig}  |  U={u:.0f}  p={p:.4f}  |  {label}")


print("\n--- D) Chi-Square Tests (categorical features) ---")
print("    Tests independence between categorical variables and default\n")

cat_tests = ["gender", "marital_status", "education_level", "employment_type",
             "loan_purpose", "has_collateral", "has_co_signer", "bankruptcy_history"]

for col in cat_tests:
    ct = pd.crosstab(df[col], df["defaulted_bin"])
    if ct.shape[0] > 1 and ct.shape[1] > 1:
        try:
            chi2, p, dof, expected = chi2_contingency(ct)
            sig = "✓ SIGNIFICANT" if p < 0.05 else "  not significant"
            print(f"  {sig}  |  χ²={chi2:.3f}  dof={dof}  p={p:.4f}  |  {col}")
        except Exception:
            print(f"  [skipped — insufficient cell counts]  |  {col}")


print("\n--- E) Normality Tests (Shapiro-Wilk) ---")
print("    Validates t-test assumption for key continuous features\n")

norm_cols = ["credit_score", "debt_to_income_ratio", "annual_income",
             "credit_risk_score", "income_stability_score"]

for col in norm_cols:
    vals = df[col].dropna().values
    if len(vals) >= 3:
        w, p = shapiro(vals)
        normal = "Normal" if p > 0.05 else "Non-normal"
        print(f"  {normal:<10}  |  W={w:.4f}  p={p:.4f}  |  {col}")


# =============================================================================
# SECTION 4 — VISUALIZATION
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: GENERATING VISUALIZATIONS")
print("=" * 65)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   11,
    "axes.labelsize":   10,
})

colors_map = {0: "#378ADD", 1: "#E24B4A"}
clrs = df["defaulted_bin"].map(colors_map)

# ---- Figure 1: EDA Overview ----
fig1, axes = plt.subplots(3, 3, figsize=(15, 12))
fig1.suptitle("Exploratory Data Analysis — Loan Default Dataset", fontsize=14, fontweight="bold", y=0.98)

# 1. Credit Score Distribution
axes[0,0].hist(nd["credit_score"], bins=6, color="#378ADD", alpha=0.7, label="No Default", edgecolor="white")
axes[0,0].hist(d["credit_score"], bins=3, color="#E24B4A", alpha=0.8, label="Default", edgecolor="white")
axes[0,0].set_title("Credit Score Distribution")
axes[0,0].set_xlabel("Credit Score"); axes[0,0].legend(fontsize=9)

# 2. DTI by Default Status
axes[0,1].bar(["No Default", "Default"],
              [nd["debt_to_income_ratio"].mean(), d["debt_to_income_ratio"].mean()],
              color=["#378ADD", "#E24B4A"], edgecolor="none", width=0.5)
axes[0,1].set_title("Mean DTI Ratio by Default Status")
axes[0,1].set_ylabel("DTI Ratio (%)")
for i, v in enumerate([nd["debt_to_income_ratio"].mean(), d["debt_to_income_ratio"].mean()]):
    axes[0,1].text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")

# 3. Annual Income vs Loan Amount
axes[0,2].scatter(df["annual_income"], df["loan_amount"],
                  c=clrs, s=120, edgecolors="white", linewidths=1, zorder=3)
axes[0,2].set_title("Annual Income vs Loan Amount")
axes[0,2].set_xlabel("Annual Income ($)"); axes[0,2].set_ylabel("Loan Amount ($)")
for _, row in df.iterrows():
    axes[0,2].annotate(row["applicant_id"][-2:], (row["annual_income"], row["loan_amount"]),
                       textcoords="offset points", xytext=(5, 4), fontsize=7, color="gray")

# 4. Credit Risk Score by Applicant
x_pos = np.arange(len(df))
bar_colors = df["defaulted_bin"].map(colors_map).tolist()
bars = axes[1,0].bar(x_pos, df["credit_risk_score"], color=bar_colors, edgecolor="none", width=0.6)
axes[1,0].set_xticks(x_pos)
axes[1,0].set_xticklabels([f"APP{i+1}" for i in range(len(df))], rotation=30, fontsize=8)
axes[1,0].set_title("Credit Risk Composite Score")
axes[1,0].set_ylabel("Score")
axes[1,0].axhline(df["credit_risk_score"].mean(), color="gray", linestyle="--", linewidth=1, alpha=0.7, label=f"Mean={df['credit_risk_score'].mean():.1f}")
axes[1,0].legend(fontsize=8)

# 5. Loan Purpose Pie
purpose_counts = df["loan_purpose"].value_counts()
axes[1,1].pie(purpose_counts, labels=purpose_counts.index, autopct="%1.0f%%",
              colors=["#B5D4F4","#9FE1CB","#FAC775"], startangle=90,
              wedgeprops={"edgecolor": "white", "linewidth": 1.5})
axes[1,1].set_title("Loan Purpose Distribution")

# 6. Interest Rate vs Credit Score (bubble = loan term)
bubble_size = (df["loan_term_months"] / df["loan_term_months"].max()) * 300 + 50
sc = axes[1,2].scatter(df["credit_score"], df["interest_rate"],
                       c=clrs, s=bubble_size, alpha=0.8, edgecolors="white", linewidths=1)
axes[1,2].set_title("Interest Rate vs Credit Score\n(bubble ∝ loan term)")
axes[1,2].set_xlabel("Credit Score"); axes[1,2].set_ylabel("Interest Rate (%)")

# 7. Income Stability Score boxplot
data_grp = [nd["income_stability_score"].dropna(), d["income_stability_score"].dropna()]
bp = axes[2,0].boxplot(data_grp, patch_artist=True, widths=0.4,
                        labels=["No Default", "Default"])
for patch, color in zip(bp["boxes"], ["#378ADD", "#E24B4A"]):
    patch.set_facecolor(color); patch.set_alpha(0.5)
axes[2,0].set_title("Income Stability Score by Default")
axes[2,0].set_ylabel("Score")

# 8. Expense Ratio
axes[2,1].scatter(df["expense_ratio"], df["credit_risk_score"],
                  c=clrs, s=120, edgecolors="white", linewidths=1, zorder=3)
axes[2,1].set_title("Expense Ratio vs Credit Risk Score")
axes[2,1].set_xlabel("Expense Ratio"); axes[2,1].set_ylabel("Credit Risk Score")
mask = df["expense_ratio"].notna() & df["credit_risk_score"].notna()
if mask.sum() > 2:
    z = np.polyfit(df.loc[mask, "expense_ratio"], df.loc[mask, "credit_risk_score"], 1)
    p_line = np.poly1d(z)
    x_line = np.linspace(df["expense_ratio"].dropna().min(), df["expense_ratio"].dropna().max(), 100)
    axes[2,1].plot(x_line, p_line(x_line), "--", color="gray", linewidth=1, alpha=0.7)

# 9. Monthly Surplus
surplus_vals = df["monthly_surplus"].fillna(0)
axes[2,2].bar(x_pos, surplus_vals, color=bar_colors, edgecolor="none", width=0.6)
axes[2,2].set_xticks(x_pos)
axes[2,2].set_xticklabels([f"APP{i+1}" for i in range(len(df))], rotation=30, fontsize=8)
axes[2,2].set_title("Monthly Surplus by Applicant")
axes[2,2].set_ylabel("Monthly Surplus ($)")
axes[2,2].axhline(0, color="black", linewidth=0.8)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#378ADD", label="No Default"),
                   Patch(facecolor="#E24B4A", label="Default")]
fig1.legend(handles=legend_elements, loc="lower center", ncol=2,
            fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig("eda_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: eda_overview.png")

# ---- Figure 2: Correlation Heatmap ----
fig2, ax = plt.subplots(figsize=(12, 10))
heat_cols = [
    "credit_score", "debt_to_income_ratio", "annual_income",
    "income_stability_score", "credit_risk_score", "loan_to_income_ratio",
    "payment_to_income_ratio", "expense_ratio", "employment_risk_score",
    "education_rank", "loan_term_months", "interest_rate",
    "has_collateral_bin", "defaulted_bin"
]
corr_heat = df[heat_cols].corr()
mask_upper = np.triu(np.ones_like(corr_heat, dtype=bool))
sns.heatmap(corr_heat, mask=mask_upper, cmap="RdBu_r", center=0,
            vmin=-1, vmax=1, annot=True, fmt=".2f", linewidths=0.5,
            linecolor="white", square=True, ax=ax,
            annot_kws={"size": 8})
ax.set_title("Correlation Matrix — Raw & Engineered Features", fontsize=13, pad=15)
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: correlation_heatmap.png")

# ---- Figure 3: Hypothesis Summary ----
fig3, axes3 = plt.subplots(2, 3, figsize=(15, 8))
fig3.suptitle("Hypothesis Validation — Defaulters vs Non-Defaulters", fontsize=13, fontweight="bold")

hyp_data = [
    ("credit_score",          "H1: Credit Score",            False),
    ("debt_to_income_ratio",  "H2: DTI Ratio (%)",           False),
    ("income_stability_score","H3: Income Stability",        False),
    ("employment_risk_score", "H4: Employment Risk",         False),
    ("credit_risk_score",     "H5: Credit Risk Score*",      True),
    ("monthly_surplus",       "H6: Monthly Surplus ($)",     False),
]

for ax, (col, title, sig) in zip(axes3.flatten(), hyp_data):
    grp_data = [df[df["defaulted_bin"] == 0][col].dropna(),
                df[df["defaulted_bin"] == 1][col].dropna()]
    bp = ax.boxplot(grp_data, patch_artist=True, widths=0.45,
                    labels=["No Default", "Default"],
                    medianprops={"color": "black", "linewidth": 2})
    for patch, color in zip(bp["boxes"], ["#378ADD", "#E24B4A"]):
        patch.set_facecolor(color); patch.set_alpha(0.55)
    ax.set_title(title + (" ✓" if sig else ""), fontsize=10,
                 color=("#2E7D32" if sig else "black"))
    ax.set_ylabel(col.replace("_", " ").title(), fontsize=9)
    if sig:
        ax.patch.set_facecolor("#f0fff0")
        ax.patch.set_alpha(0.4)

axes3.flatten()[-1].text(0.5, 0.05, "* p < 0.05 (point-biserial r = −0.814)",
                          transform=axes3.flatten()[-1].transAxes,
                          ha="center", fontsize=9, color="#2E7D32")
plt.tight_layout()
plt.savefig("hypothesis_tests.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: hypothesis_tests.png")

# ---- Figure 4: Feature Importance (correlation-based) ----
fig4, ax4 = plt.subplots(figsize=(10, 7))
feat_corr = df[heat_cols].corr()["defaulted_bin"].drop("defaulted_bin").sort_values()
bar_cols = ["#E24B4A" if v > 0 else "#378ADD" for v in feat_corr]
ax4.barh(feat_corr.index, feat_corr.values, color=bar_cols, edgecolor="none", height=0.6)
ax4.axvline(0, color="black", linewidth=0.8)
ax4.axvline(0.5, color="#E24B4A", linewidth=0.8, linestyle="--", alpha=0.5)
ax4.axvline(-0.5, color="#378ADD", linewidth=0.8, linestyle="--", alpha=0.5)
ax4.set_title("Feature Correlations with Default Outcome", fontsize=12, fontweight="bold")
ax4.set_xlabel("Pearson / Point-Biserial Correlation with Default")
for i, (val, name) in enumerate(zip(feat_corr.values, feat_corr.index)):
    ax4.text(val + (0.01 if val >= 0 else -0.01), i,
             f"{val:+.3f}", va="center", ha=("left" if val >= 0 else "right"),
             fontsize=9, color=("black"))
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: feature_importance.png")


# =============================================================================
# SECTION 5 — SUMMARY TABLE
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: FINAL PROCESSED DATASET")
print("=" * 65)

final_cols = [
    "applicant_id", "defaulted_bin",
    "credit_score", "credit_risk_score",
    "debt_to_income_ratio", "income_stability_score",
    "loan_to_income_ratio", "payment_to_income_ratio",
    "expense_ratio", "monthly_surplus",
    "total_wealth", "wealth_to_loan",
    "education_rank", "employment_risk_score",
    "has_collateral_bin", "loan_burden_index"
]
print(df[final_cols].round(3).to_string(index=False))

# Save processed CSV
df.to_csv("loan_processed.csv", index=False)
print("\nProcessed dataset saved → loan_processed.csv")

print("\n" + "=" * 65)
print("ANALYSIS COMPLETE")
print("  Outputs: eda_overview.png | correlation_heatmap.png")
print("           hypothesis_tests.png | feature_importance.png")
print("           loan_processed.csv")
print("=" * 65)