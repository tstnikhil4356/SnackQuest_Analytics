"""
Notebook 03: Stock-Out Loss Quantification
------------------------------------------
Objective: Calculate the financial impact of stock-out situations by
comparing healthy stock performance against at-risk periods.
"""

import pandas as pd
import numpy as np

print("-" * 70)
print("NOTEBOOK 03: STOCK-OUT LOSS QUANTIFICATION")
print("-" * 70)

# --- STEP 1: LOAD MASTER DATASET ---
print("\n[1/10] LOADING MASTER DATASET...")
try:
    master = pd.read_csv('../data/master_dataset.csv', parse_dates=['Date'])
    total_revenue = master['Revenue'].sum()

    print(f"Transactions:    {len(master):,}")
    print(f"Date Range:      {master['Date'].min().date()} to {master['Date'].max().date()}")
    print(f"Total Revenue:   ${total_revenue:,.2f}")
except FileNotFoundError as e:
    print(f"Error: {e}")

# --- STEP 2: BASELINE PERFORMANCE (HEALTHY STOCK) ---
print("\n[2/10] ESTABLISHING BASELINE (HEALTHY STOCK)")
healthy = master[master['Stock_Risk'] == False]
healthy_pct = (len(healthy) / len(master)) * 100

print(f"Healthy transactions: {len(healthy):,} ({healthy_pct:.1f}%)")

baseline = healthy.groupby('SKU').agg({
    'Units_Sold': ['mean', 'std'],
    'Price': 'mean',
    'Revenue': 'sum'
}).round(2)

baseline.columns = ['Avg_Units_Healthy', 'StdDev_Units', 'Avg_Price', 'Healthy_Revenue']
print("\nBaseline metrics by product:")
print(baseline.head())

# --- STEP 3: AT-RISK PERFORMANCE ---
print("\n[3/10] ANALYZING AT-RISK TRANSACTIONS")
at_risk = master[master['Stock_Risk'] == True]
risk_pct = (len(at_risk) / len(master)) * 100

print(f"At-Risk transactions: {len(at_risk):,} ({risk_pct:.1f}%)")

risk_perf = at_risk.groupby('SKU').agg({
    'Units_Sold': ['mean', 'count'],
    'Revenue': 'sum'
}).round(2)

risk_perf.columns = ['Avg_Units_AtRisk', 'Risk_Transactions', 'AtRisk_Revenue']

# --- STEP 4: QUANTIFY LOST OPPORTUNITY ---
print("\n[4/10] CALCULATING LOST SALES OPPORTUNITY")
# Assumption: 30% loss rate during at-risk periods
LOSS_RATE = 0.30

loss_analysis = baseline.copy().join(risk_perf)

loss_analysis['Potential_Lost_Units'] = (
        loss_analysis['Risk_Transactions'] * loss_analysis['Avg_Units_Healthy'] * LOSS_RATE
)

loss_analysis['Potential_Lost_Revenue'] = (
        loss_analysis['Potential_Lost_Units'] * loss_analysis['Avg_Price']
)

loss_analysis = loss_analysis.sort_values('Potential_Lost_Revenue', ascending=False)

# --- STEP 5: TOTAL IMPACT ---
print("\n[5/10] TOTAL STOCK-OUT IMPACT SUMMARY")
total_lost_revenue = loss_analysis['Potential_Lost_Revenue'].sum()
total_lost_units = loss_analysis['Potential_Lost_Units'].sum()
loss_to_rev_ratio = (total_lost_revenue / total_revenue) * 100

print(f"Monthly Actual Revenue:    ${total_revenue:,.2f}")
print(f"Estimated Lost Revenue:    ${total_lost_revenue:,.2f}")
print(f"Revenue Loss Percentage:   {loss_to_rev_ratio:.2f}%")
print(f"Estimated Lost Units:      {total_lost_units:,.0f}")

# --- STEP 6: ANNUALIZED PROJECTION ---
print("\n[6/10] ANNUALIZED PROJECTION")
annual_lost_revenue = total_lost_revenue * 12

print(f"Current Monthly Loss:      ${total_lost_revenue:,.2f}")
print(f"Projected Annual Loss:     ${annual_lost_revenue:,.2f}")

# --- STEP 7: RECOVERY RECOMMENDATIONS ---
print("\n[7/10] STRATEGIC RECOVERY ACTIONS")
print("1. Optimize reorder points for high-velocity SKUs")
print("2. Establish safety stock buffers for Granola category")
print("3. Implement automated low-stock triggers")
print("4. Audit replenishment lead times")

# --- STEP 8: PRODUCT-SPECIFIC PRIORITIES ---
print("\n[8/10] HIGH-PRIORITY RECOVERY TARGETS")
for i, (product, row) in enumerate(loss_analysis.head(5).iterrows(), 1):
    impact = row['Potential_Lost_Revenue']
    share = (impact / total_lost_revenue) * 100
    priority = "HIGH" if i <= 2 else "MEDIUM"

    print(f"{i}. {product:.<20} ${impact:,.2f} ({share:.1f}% of total) [Priority: {priority}]")

# --- STEP 9: SENSITIVITY ANALYSIS ---
print("\n[9/10] SENSITIVITY ANALYSIS (LOSS RATE VARIANCES)")
for rate in [0.20, 0.30, 0.40]:
    adj_loss = (loss_analysis['Risk_Transactions'] * loss_analysis['Avg_Units_Healthy'] * rate * loss_analysis[
        'Avg_Price']).sum()
    print(f"Rate {int(rate * 100)}%: Monthly Loss = ${adj_loss:,.2f}")

# --- STEP 10: EXPORT RESULTS ---
print("\n[10/10] EXPORTING ANALYSIS")
loss_analysis.to_csv('../data/stockout_loss_analysis.csv')

summary_data = {
    'Analysis_Date': [pd.Timestamp.now().date()],
    'Monthly_Loss_USD': [total_lost_revenue],
    'Annual_Loss_USD': [annual_lost_revenue],
    'Loss_Pct': [loss_to_rev_ratio]
}
pd.DataFrame(summary_data).to_csv('../data/stockout_summary.csv', index=False)
print("Analysis exported to /data/ directory.")

print("\n" + "-" * 70)
print("NOTEBOOK 03 PROCESSING COMPLETE")
print("-" * 70)