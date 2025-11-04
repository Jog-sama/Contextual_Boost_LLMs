# Assumption Checks for McNemar’s Test and Paired t-test

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from scipy.stats import shapiro, ttest_rel, wilcoxon , probplot
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.power import TTestPower
from scipy.stats import norm, t

# load data
df = pd.read_excel("gpqa_results.xlsx")   
if 'is_correct' not in df.columns:
    df['is_correct'] = (df['model_answer'] == df['correct_option']).astype(int)

# pivot to get one row per question with role / normal columns
pivot = df.pivot(index='id', columns='prompt_type', values='is_correct').dropna()
pivot.columns = [c.lower() for c in pivot.columns]

# Independence 

n_unique_ids = pivot.index.nunique()
n_total = len(pivot)
if n_unique_ids == n_total:
    print(f"Independence check: {n_unique_ids} unique question IDs (no duplicates).")
else:
    print(f"check for duplicates")

# McNemar discordant-pair check

b = int(((pivot['role'] == 1) & (pivot['normal'] == 0)).sum())
c = int(((pivot['role'] == 0) & (pivot['normal'] == 1)).sum())
print(f"Discordant pairs: b={b}, c={c}")
discordant = b + c
print(f"Discordant pairs (b+c): {discordant}")

# QQ plot for visual normality check
plt.figure(figsize=(5,5))
pivot['role'] = pivot['role'].astype(int)
pivot['normal'] = pivot['normal'].astype(int)

diff = pivot['role'] - pivot['normal']   # values in {-1,0,1}
probplot(diff, dist="norm", plot=plt)
plt.title("QQ Plot of Paired Differences (Role − No-role)")
plt.show()


# Paired t-test power 
from statsmodels.stats.power import TTestPower, TTestIndPower
import math

m = 0.07  # expected absolute difference (7 percentage points)
sd_list = [0.20, 0.25, 0.30, 0.35]  # plausible sd of paired differences
tp = TTestPower()
ind = TTestIndPower()

for sd in sd_list:
    d = m / sd
    n_pairs = math.ceil(tp.solve_power(effect_size=d, power=0.8, alpha=0.05))
    n_per_group_indep = math.ceil(ind.solve_power(effect_size=d, power=0.8, alpha=0.05, alternative='two-sided'))
    print(f"sd={sd:.2f} -> d={d:.3f} -> pairs needed (paired)={n_pairs}, per-group (indep)={n_per_group_indep}")


# contingency table (a,b,c,d)
a = int(((pivot['role'] == 1) & (pivot['normal'] == 1)).sum())
b = int(((pivot['role'] == 1) & (pivot['normal'] == 0)).sum())  # role-only
c = int(((pivot['role'] == 0) & (pivot['normal'] == 1)).sum())  # no-role-only
d = int(((pivot['role'] == 0) & (pivot['normal'] == 0)).sum())
N = len(pivot)
print("Contingency table (a,b;c,d):", [[a,b],[c,d]])

# McNemar exact test 
mcnemar_res = mcnemar(np.array([[a,b],[c,d]]), exact=True)
print("McNemar exact p-value:", mcnemar_res.pvalue)

# descriptive rates and risk diff
p_role = (a + b) / N
p_no = (a + c) / N
risk_diff = p_role - p_no
print(f"Role accuracy: {p_role:.3f}, No-role accuracy: {p_no:.3f}, Risk diff: {risk_diff:.3f}")

# paired differences (for t/Wilcoxon & effect sizes)
pivot['role'] = pivot['role'].astype(int)
pivot['normal'] = pivot['normal'].astype(int)

diff = pivot['role'] - pivot['normal']   # values in {-1,0,1}
mean_diff = diff.mean()
sd_diff = diff.std(ddof=1)
se = sd_diff / math.sqrt(N)

# 95% CI for mean diff (t dist)

tcrit = t.ppf(0.975, df=N-1)
ci_low = mean_diff - tcrit * se
ci_high = mean_diff + tcrit * se
print("Mean diff:", mean_diff, "SD diff:", sd_diff, "95% CI:", (ci_low, ci_high))

# Wilcoxon (nonparametric) and paired t-test
wil_stat, wil_p = wilcoxon(pivot['role'], pivot['normal'], alternative='two-sided')
t_stat, t_p = ttest_rel(pivot['role'], pivot['normal'])
print("Wilcoxon W:", wil_stat, "p:", wil_p)
print("Paired t-stat:", t_stat, "p:", t_p)

# effect sizes
# Cohen's h for proportions
h = 2*(math.asin(math.sqrt(p_role)) - math.asin(math.sqrt(p_no)))
# Discordant OR
discord_or = b / c if c != 0 else float('inf')
# Paired Cohen's d
cohens_d = mean_diff / sd_diff if sd_diff != 0 else 0.0
print("Cohen's h:", h, "Discordant OR (b/c):", discord_or, "Cohen's d (paired):", cohens_d)


# Report summary (print)
summary = {
    'N_pairs': N, 'a':a,'b':b,'c':c,'d':d,
    'p_role':p_role, 'p_no':p_no, 'risk_diff':risk_diff,
    'wilcoxon_p':wil_p, 'paired_t_p':t_p,
    'cohens_h':h, 'cohens_d':cohens_d
}
print(summary)
