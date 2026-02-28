"""
NOTEBOOK 04: PROMOTION ROI ANALYSIS
====================================

Purpose: Calculate TRUE cost of promotions and identify waste

Key Question: Is BOGO destroying margins or adding value?

Business Logic:
- BOGO = Buy One Get One = 50% discount (give away half)
- 10% Discount = 10% discount
- Which generates more profit after discount costs?

Time: 30 minutes
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("NOTEBOOK 04: PROMOTION ROI ANALYSIS")
print("=" * 70)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("\n[1/9] LOADING MASTER DATASET...")
master = pd.read_csv('../data/master_dataset.csv', parse_dates=['Date'])

total_revenue = master['Revenue'].sum()
print(f"Total Revenue: ${total_revenue:,.2f}")

# ============================================================================
# STEP 2: GROSS REVENUE BY PROMOTION
# ============================================================================

print("\n" + "=" * 70)
print("[2/9] GROSS REVENUE BY PROMOTION TYPE")
print("=" * 70)

promo_summary = master.groupby('Promotion').agg({
    'Revenue': 'sum',
    'Units_Sold': 'sum',
    'Date': 'count'
}).rename(columns={'Date': 'Transactions'})

print("\nGross Performance:")
print(promo_summary)

# ============================================================================
# STEP 3: CALCULATE TRUE DISCOUNT COST
# ============================================================================

print("\n" + "=" * 70)
print("[3/9] CALCULATING TRUE DISCOUNT COSTS")
print("=" * 70)

print("\nDISCOUNT METHODOLOGY:")
print("-" * 70)
print("BOGO (Buy One Get One):")
print("  Customer pays for 1 unit, gets 2 units")
print("  Effective discount = 50% (half the units are free)")
print("  Discount Cost = Gross Revenue x 0.50")
print()
print("10% Discount:")
print("  Customer gets 10% off")
print("  Discount Cost = Gross Revenue x 0.10")
print()
print("None (No Promotion):")
print("  No discount given")
print("  Discount Cost = $0")
print("-" * 70)

# Calculate discount costs
results = []

for promo in promo_summary.index:
    gross_revenue = promo_summary.loc[promo, 'Revenue']
    units = promo_summary.loc[promo, 'Units_Sold']
    transactions = promo_summary.loc[promo, 'Transactions']

    # Determine discount rate
    if promo == 'BOGO':
        discount_rate = 0.50  # 50% discount
    elif '10%' in promo:
        discount_rate = 0.10  # 10% discount
    else:
        discount_rate = 0.00  # No discount

    # Calculate costs and net revenue
    discount_cost = gross_revenue * discount_rate
    net_revenue = gross_revenue - discount_cost

    # Calculate ROI
    if discount_cost > 0:
        # ROI = (Net Revenue / Discount Cost) x 100
        roi = (net_revenue / discount_cost) * 100
    else:
        roi = 0  # No cost, no ROI calculation

    results.append({
        'Promotion': promo,
        'Transactions': transactions,
        'Units_Sold': units,
        'Gross_Revenue': gross_revenue,
        'Discount_Rate': discount_rate,
        'Discount_Cost': discount_cost,
        'Net_Revenue': net_revenue,
        'ROI_Percent': roi
    })

results_df = pd.DataFrame(results)

# ============================================================================
# STEP 4: DISPLAY PROMOTION ECONOMICS
# ============================================================================

print("\n" + "=" * 70)
print("[4/9] PROMOTION ECONOMICS BREAKDOWN")
print("=" * 70)

for _, row in results_df.iterrows():
    print(f"\n{row['Promotion']}:")
    print(f"  Transactions:     {int(row['Transactions']):,}")
    print(f"  Units Sold:       {int(row['Units_Sold']):,}")
    print(f"  Gross Revenue:    ${row['Gross_Revenue']:,.2f}")
    print(f"  Discount Rate:    {row['Discount_Rate'] * 100:.0f}%")
    print(f"  Discount Cost:    ${row['Discount_Cost']:,.2f}")
    print(f"  NET REVENUE:      ${row['Net_Revenue']:,.2f}")
    if row['ROI_Percent'] > 0:
        print(f"  ROI:              {row['ROI_Percent']:.1f}%")

# ============================================================================
# STEP 5: COMPARE BOGO VS 10% DISCOUNT
# ============================================================================

print("\n" + "=" * 70)
print("[5/9] BOGO VS 10% DISCOUNT COMPARISON")
print("=" * 70)

bogo_row = results_df[results_df['Promotion'] == 'BOGO'].iloc[0]
discount_row = results_df[results_df['Promotion'] == '10%_Discount'].iloc[0]

print("\nDIRECT COMPARISON:")
print("-" * 70)
print(f"                      BOGO          10% Discount")
print(f"Gross Revenue:        ${bogo_row['Gross_Revenue']:>12,.2f}  ${discount_row['Gross_Revenue']:>12,.2f}")
print(f"Discount Cost:        ${bogo_row['Discount_Cost']:>12,.2f}  ${discount_row['Discount_Cost']:>12,.2f}")
print(f"Net Revenue:          ${bogo_row['Net_Revenue']:>12,.2f}  ${discount_row['Net_Revenue']:>12,.2f}")
print(f"ROI:                  {bogo_row['ROI_Percent']:>12.1f}%  {discount_row['ROI_Percent']:>12.1f}%")
print("-" * 70)

# Calculate which is better
roi_difference = discount_row['ROI_Percent'] - bogo_row['ROI_Percent']
net_revenue_difference = discount_row['Net_Revenue'] - bogo_row['Net_Revenue']

print(f"\nKEY FINDING:")
print(f"10% Discount has {roi_difference:.0f}% HIGHER ROI than BOGO")
print(f"10% Discount generates ${net_revenue_difference:,.2f} MORE net revenue")

# ============================================================================
# STEP 6: IDENTIFY PROMOTION WASTE
# ============================================================================

print("\n" + "=" * 70)
print("[6/9] QUANTIFYING PROMOTION INEFFICIENCY")
print("=" * 70)

print("\nSCENARIO ANALYSIS:")
print("-" * 70)
print("What if we replaced ALL BOGO with 10% Discount?")
print()

# Current state
current_bogo_cost = bogo_row['Discount_Cost']
current_total_cost = results_df['Discount_Cost'].sum()

# Alternative: If BOGO transactions used 10% discount instead
bogo_revenue = bogo_row['Gross_Revenue']
alternative_bogo_cost = bogo_revenue * 0.10

# Calculate savings
promotion_waste = current_bogo_cost - alternative_bogo_cost
waste_pct = (promotion_waste / total_revenue) * 100

print(f"Current BOGO cost:               ${current_bogo_cost:,.2f}")
print(f"If using 10% discount instead:   ${alternative_bogo_cost:,.2f}")
print(f"MONTHLY WASTE:                   ${promotion_waste:,.2f}")
print(f"As % of revenue:                 {waste_pct:.2f}%")

# ============================================================================
# STEP 7: ANNUAL IMPACT
# ============================================================================

print("\n" + "=" * 70)
print("[7/9] ANNUALIZED PROMOTION WASTE")
print("=" * 70)

annual_waste = promotion_waste * 12

print(f"\nMonthly promotion waste:    ${promotion_waste:,.2f}")
print(f"Annual promotion waste:     ${annual_waste:,.2f}")
print(f"Margin impact:              {waste_pct:.2f}%")

# ============================================================================
# STEP 8: RECOMMENDATIONS
# ============================================================================

print("\n" + "=" * 70)
print("[8/9] STRATEGIC RECOMMENDATIONS")
print("=" * 70)

print("\nRECOMMENDATIONS:")
print("-" * 70)
print("1. STOP blanket BOGO campaigns")
print(f"   Current cost: ${current_bogo_cost:,.2f}/month")
print(f"   Better alternative: 10% discount")
print()
print("2. USE BOGO strategically only for:")
print("   - New product trials (limited time)")
print("   - Slow-moving inventory clearance")
print("   - NOT for regular promotions")
print()
print("3. DEFAULT to 10% discount")
print(f"   {roi_difference:.0f}% better ROI")
print(f"   Generates ${net_revenue_difference:,.2f} more net revenue")
print()
print("4. EXPECTED RECOVERY")
print(f"   Monthly savings: ${promotion_waste:,.2f}")
print(f"   Annual savings: ${annual_waste:,.2f}")
print(f"   Margin recovery: {waste_pct:.2f}%")

# ============================================================================
# STEP 9: SAVE RESULTS
# ============================================================================

print("\n" + "=" * 70)
print("[9/9] SAVING ANALYSIS RESULTS")
print("=" * 70)

# Save detailed results
results_df.to_csv('../outputs/promotion_roi_analysis.csv', index=False)
print("Saved: promotion_roi_analysis.csv")

# Create summary
summary = {
    'Analysis_Date': pd.Timestamp.now().strftime('%Y-%m-%d'),
    'BOGO_Gross_Revenue': bogo_row['Gross_Revenue'],
    'BOGO_Discount_Cost': bogo_row['Discount_Cost'],
    'BOGO_Net_Revenue': bogo_row['Net_Revenue'],
    'BOGO_ROI': bogo_row['ROI_Percent'],
    'Discount10_Gross_Revenue': discount_row['Gross_Revenue'],
    'Discount10_Discount_Cost': discount_row['Discount_Cost'],
    'Discount10_Net_Revenue': discount_row['Net_Revenue'],
    'Discount10_ROI': discount_row['ROI_Percent'],
    'ROI_Difference': roi_difference,
    'Monthly_Waste': promotion_waste,
    'Annual_Waste': annual_waste,
    'Waste_Pct_Revenue': waste_pct
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('../outputs/promotion_summary.csv', index=False)
print("Saved: promotion_summary.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("FINAL SUMMARY - PROMOTION ANALYSIS")
print("=" * 70)

print(f"""
KEY FINDINGS:
-------------
1. BOGO ROI:           {bogo_row['ROI_Percent']:.1f}%
2. 10% Discount ROI:   {discount_row['ROI_Percent']:.1f}%
3. Difference:         {roi_difference:.0f}% (10% is better)

FINANCIAL IMPACT:
-----------------
Monthly waste from BOGO:     ${promotion_waste:,.2f}
Annual waste from BOGO:      ${annual_waste:,.2f}
Margin impact:               {waste_pct:.2f}%

BUSINESS DECISION:
------------------
Replace BOGO with 10% Discount
Expected recovery: {waste_pct:.2f}% of margin

PROGRESS TRACKING:
------------------
Stock-out loss:       ~6.3% (from Notebook 03)
Promotion waste:      ~{waste_pct:.1f}% (current analysis)
TOTAL IDENTIFIED:     ~{6.3 + waste_pct:.1f}%
TARGET:               4.0%

NOTE: Total > 4% means these are MAJOR drivers
Next: Check if there are offsetting factors
""")

print("=" * 70)
print("NOTEBOOK 04 COMPLETE")
print("=" * 70)