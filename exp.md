Imports
pythonimport pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from scipy.stats import (ttest_ind, pointbiserialr, chi2_contingency,
                          mannwhitneyu, shapiro, pearsonr)
Each library has a specific role. pandas handles the dataframe (table operations, grouping, filtering). numpy handles numerical computation (array math, np.where, np.polyfit). matplotlib and seaborn handle all plotting. scipy.stats provides every statistical test used in Section 3. warnings.filterwarnings("ignore") just suppresses minor runtime warnings so the output stays clean.

Data Loading
pythondata = { "applicant_id": [...], "age": [...], ... }
df = pd.DataFrame(data)
df["application_date"] = pd.to_datetime(df["application_date"])
The raw data is stored as a Python dictionary where each key is a column name and each value is a list of 7 entries (one per applicant). pd.DataFrame(data) converts it into a table. The application_date column is explicitly converted to a proper datetime type so pandas can extract month, quarter, etc. from it later. np.nan is used for the two missing values (APP5's savings and monthly expenses).

Section 1 — Feature Engineering
This is the most important section. Raw columns alone aren't always useful for analysis — you need to derive more meaningful signals from them.
Binary Encoding
pythondf["has_co_signer_bin"] = np.where(df["has_co_signer"] == "Yes", 1, 0)
df["defaulted_bin"]     = np.where(df["defaulted"] == "Yes", 1, 0)
np.where(condition, value_if_true, value_if_false) converts text columns like "Yes"/"No" into 1/0 integers. This is necessary because statistical tests and correlation calculations require numbers, not strings. Every Yes/No column (co-signer, collateral, bankruptcy, direct deposit, defaulted) gets this treatment.
Ordinal Encoding
pythonedu_map = {"High School": 1, "Bachelor": 2, "Master": 3, "PhD": 4}
df["education_rank"] = df["education_level"].map(edu_map)

emp_risk_map = {"Full-time": 1, "Part-time": 2, ..., "Unemployed": 5}
df["employment_risk_score"] = df["employment_type"].map(emp_risk_map)
These columns have a natural order (more education = higher rank, unemployed = higher risk), so they're encoded as ordered numbers using .map() on a dictionary. This preserves the meaningful ranking that plain label encoding wouldn't capture.
Financial Ratio Features
pythondf["monthly_surplus"]          = df["monthly_income"] - df["monthly_expenses"]
df["loan_to_income_ratio"]     = df["loan_amount"] / df["annual_income"]
df["payment_to_income_ratio"]  = df["monthly_loan_payment_est"] / df["monthly_income"]
df["expense_ratio"]            = df["monthly_expenses"] / df["monthly_income"]
These are derived by simple arithmetic on existing columns. monthly_surplus tells you how much money someone has left after expenses — a key indicator of repayment ability. loan_to_income_ratio shows how large the loan is relative to what someone earns. expense_ratio shows what fraction of income is already spent. pandas lets you do column-level arithmetic directly like numpy arrays.
Wealth Features
pythondf["total_liquid_assets"] = df["savings_balance"].fillna(0) + df["checking_balance"].fillna(0)
df["total_wealth"]        = df["total_liquid_assets"] + df["investment_portfolio_value"].fillna(0)
df["wealth_to_loan"]      = df["total_wealth"] / df["loan_amount"]
.fillna(0) replaces missing values with 0 before adding, so APP5's missing savings don't produce NaN for the entire row. wealth_to_loan tells you how much of the loan could theoretically be covered by the applicant's own assets.
Credit Risk Composite Score
pythondf["credit_risk_score"] = (
    (df["credit_score"] / 850) * 40
    + (1 - df["debt_to_income_ratio"] / 100) * 30
    + (df["income_stability_score"] / 10) * 30
)
This manually constructs a single score by normalising three important features and weighting them. Credit score is divided by the max (850) to get a 0–1 scale, then multiplied by 40 (its weight). DTI is inverted — higher DTI is worse, so 1 - DTI/100 means lower DTI gives a higher score — then weighted 30. Income stability is divided by 10 (its max) and weighted 30. The result is a score out of 100. This turns out to be the strongest predictor of default in the dataset.
Date Features
pythondf["app_month"]       = df["application_date"].dt.month
df["app_quarter"]     = df["application_date"].dt.quarter
df["app_day_of_week"] = df["application_date"].dt.dayofweek
.dt is pandas' datetime accessor — it lets you extract parts of a date. These features can reveal seasonal patterns (e.g., do people who apply in December default more?).
Interaction Terms
pythondf["dti_x_employment_risk"] = df["debt_to_income_ratio"] * df["employment_risk_score"]
df["loan_burden_index"]      = df["payment_to_income_ratio"] * df["employment_risk_score"]
Interaction terms multiply two features together to capture their combined effect. Someone with high DTI and high employment risk is much riskier than either factor alone — multiplying them creates a feature that encodes this amplification.

Section 2 — Exploratory Data Analysis
Descriptive Statistics
pythondf[numeric_raw].describe().round(2)
.describe() computes count, mean, std, min, 25th percentile, median, 75th percentile, and max for every column in one call. .round(2) keeps the output clean. This gives you an immediate sense of scale and spread for every feature.
Default Group Comparison
pythondefault_grp    = df[df["defaulted_bin"] == 1]
no_default_grp = df[df["defaulted_bin"] == 0]

comparison_df = pd.DataFrame({
    "Defaulter Mean":     default_grp[compare_cols].mean().round(3),
    "Non-Defaulter Mean": no_default_grp[compare_cols].mean().round(3),
    "Difference":         (...).round(3),
})
The dataframe is split into two groups by filtering on defaulted_bin. Then .mean() is computed for each group across all key columns and assembled into a side-by-side comparison table. This is the clearest way to see which features differ most between the two groups.
Categorical Breakdown
pythondf.groupby(col)["defaulted_bin"].agg(["count", "sum", "mean"])
.groupby() groups rows by a categorical column, then .agg() computes multiple statistics at once. count = total applicants in that group, sum = number of defaults, mean = default rate. This shows, for example, whether unemployed applicants default more than full-time ones.
Correlation Matrix
pythoncorr_matrix = df[corr_cols].corr()
default_corr = corr_matrix["defaulted_bin"].drop("defaulted_bin").sort_values(key=abs, ascending=False)
.corr() computes pairwise Pearson correlation coefficients for all numeric columns. Selecting the "defaulted_bin" column gives you one correlation value per feature with the target variable. sort_values(key=abs) sorts by absolute value so the strongest relationships (positive or negative) appear first.

Section 3 — Hypothesis Testing
Each hypothesis is a specific claim about the data that is validated using a statistical test.
A) Welch t-tests
pythont1, p1 = ttest_ind(d["credit_score"], nd["credit_score"], equal_var=False)
A t-test checks whether the means of two groups are statistically different. equal_var=False uses Welch's version, which doesn't assume both groups have the same variance — safer for small, unequal samples. It returns a t-statistic (how many standard errors apart the means are) and a p-value (probability of seeing this difference by chance). If p < 0.05, the difference is statistically significant. With only 7 samples, most tests don't reach significance — but the direction of every result still confirms the expected pattern.
B) Point-Biserial Correlation
pythonr, p = pointbiserialr(tgt_clean, col_clean)
Used when one variable is continuous (like credit score) and the other is binary (defaulted: 0 or 1). It's mathematically equivalent to Pearson correlation but designed for this mixed case. r ranges from -1 to +1. The credit_risk_score gives r = -0.814 with p = 0.026 — the only result that's statistically significant with this sample size.
C) Mann-Whitney U Tests
pythonu, p = mannwhitneyu(a, b, alternative="two-sided")
A non-parametric alternative to the t-test — it doesn't assume the data follows a normal distribution. Instead of comparing means, it compares rank orderings. With n=7, this is actually more appropriate than the t-test since you can't reliably verify normality. It answers: "are values in one group systematically higher than the other?"
D) Chi-Square Tests
pythonct = pd.crosstab(df[col], df["defaulted_bin"])
chi2, p, dof, expected = chi2_contingency(ct)
Used for categorical features (gender, employment type, loan purpose, etc.). pd.crosstab builds a frequency table — rows are categories, columns are 0/1 default status. chi2_contingency tests whether the distribution across categories is independent of default status, or whether certain categories are associated with higher default rates.
E) Shapiro-Wilk Normality Test
pythonw, p = shapiro(vals)
This tests whether a feature follows a normal (bell-curve) distribution. The t-test assumes normality, so this validates that assumption. If p > 0.05, the data is consistent with being normal. Most features here pass, which confirms the t-tests are reasonably appropriate.

Section 4 — Visualizations
Figure 1 — EDA Overview (3×3 grid)
pythonfig1, axes = plt.subplots(3, 3, figsize=(15, 12))
Creates a 3-row × 3-column grid of subplots. Each axes[row, col] is an individual chart. The 9 plots cover: credit score histogram, DTI bar chart, income vs loan scatter, credit risk bar chart, loan purpose pie, interest rate vs credit score bubble chart, income stability boxplot, expense ratio scatter, and monthly surplus bar chart. Red = defaulter, blue = non-defaulter throughout.
Figure 2 — Correlation Heatmap
pythonmask_upper = np.triu(np.ones_like(corr_heat, dtype=bool))
sns.heatmap(corr_heat, mask=mask_upper, cmap="RdBu_r", center=0, annot=True)
np.triu creates a boolean mask for the upper triangle so only the lower triangle is shown (avoids duplicate information). cmap="RdBu_r" uses red for positive correlation and blue for negative. center=0 anchors the colour scale at zero. annot=True prints the actual values inside each cell.
Figure 3 — Hypothesis Boxplots
pythonbp = ax.boxplot(grp_data, patch_artist=True, ...)
Six side-by-side boxplots, one per hypothesis. Each shows the distribution of a feature split by default status. patch_artist=True allows the boxes to be filled with colour. The one statistically significant hypothesis (H5, credit risk score) gets a green title with a ✓ mark.
Figure 4 — Feature Importance
pythonfeat_corr = df[heat_cols].corr()["defaulted_bin"].drop("defaulted_bin").sort_values()
ax4.barh(feat_corr.index, feat_corr.values, color=bar_cols)
A horizontal bar chart sorted by correlation value. Blue bars = protective features (negative correlation, reduces default risk). Red bars = risk features (positive correlation, increases default risk). This is the clearest single summary of which features matter most.

Section 5 — Output
pythondf.to_csv("loan_processed.csv", index=False)
Saves the full dataframe — original columns plus all engineered features — to a CSV file. index=False prevents pandas from writing the row numbers as an extra column. The four plot files are saved with plt.savefig("name.png", dpi=150, bbox_inches="tight") — dpi=150 gives good resolution without huge file sizes, and bbox_inches="tight" trims whitespace around the figure.

Key Takeaway
The most important finding the code produces is that the credit risk composite score (the engineered feature combining credit score + DTI + income stability) has a point-biserial correlation of r = −0.814, p = 0.026 with default — the only statistically significant result. This validates the feature engineering step: individual features weren't strong enough alone, but combining them into a weighted score revealed a strong, significant signal.
