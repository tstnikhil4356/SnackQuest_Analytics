"""
Notebook 02: Data Cleaning & Master Dataset Creation
----------------------------------------------------
Objective: Clean raw data, perform feature engineering, and merge
datasets into a single master file for analysis.
"""

import pandas as pd
import numpy as np

print("-" * 70)
print("NOTEBOOK 02: MASTER DATASET PREPARATION")
print("-" * 70)

# --- STEP 1: LOAD DATA ---
print("\n[1/11] LOADING DATASETS...")
try:
    sales = pd.read_csv('../data/sales_data.csv')
    inventory = pd.read_csv('../data/inventory_data.csv')
    customers = pd.read_csv('../data/customer_data.csv')

    print(f"Sales records:     {len(sales):,}")
    print(f"Inventory records: {len(inventory):,}")
    print(f"Customer records:  {len(customers):,}")
except FileNotFoundError as e:
    print(f"Error: Could not find data files. {e}")

# --- STEP 2: HANDLE MISSING PROMOTIONS ---
print("\n[2/11] CLEANING: PROMOTION DATA")
null_promos = sales['Promotion'].isnull().sum()
print(f"Initial missing values: {null_promos}")

# Fill NaNs with 'None' to represent standard transactions
sales['Promotion'] = sales['Promotion'].fillna('None')
print(f"Current missing values: {sales['Promotion'].isnull().sum()}")
print("Promotion distribution:")
print(sales['Promotion'].value_counts())

# --- STEP 3: TEMPORAL FEATURE ENGINEERING ---
print("\n[3/11] EXTRACTING TIME FEATURES")
sales['Date'] = pd.to_datetime(sales['Date'])

sales['DayOfWeek'] = sales['Date'].dt.dayofweek
sales['DayName'] = sales['Date'].dt.day_name()
sales['Week'] = sales['Date'].dt.isocalendar().week
sales['Day'] = sales['Date'].dt.day

print("Features added: DayOfWeek, DayName, Week, Day")
print("Volume by day of week:")
print(sales['DayName'].value_counts().sort_index())

# --- STEP 4: REVENUE CALCULATION ---
print("\n[4/11] CALCULATING REVENUE")
sales['Revenue'] = sales['Price'] * sales['Units_Sold']
print(f"Total Revenue: ${sales['Revenue'].sum():,.2f}")

# --- STEP 5: DATA INTEGRATION (MERGE) ---
print("\n[5/11] MERGING SALES AND INVENTORY")
master = sales.merge(
    inventory,
    on=['StoreID', 'SKU'],
    how='left'
)

# Validation logic
if len(master) == len(sales):
    print("Merge Status: Success (Row count maintained)")
else:
    print(f"Merge Status: Warning (Row count changed from {len(sales)} to {len(master)})")

# --- STEP 6: STOCK RISK INDICATORS ---
print("\n[6/11] FLAG STOCK RISK TRANSACTIONS")
# Risk defined as Stock On Hand <= Reorder Point
master['Stock_Risk'] = master['Stock_On_Hand'] <= master['Reorder_Point']

risk_count = master['Stock_Risk'].sum()
risk_pct = (risk_count / len(master)) * 100

print(f"Transactions at risk: {risk_count:,}")
print(f"Risk Percentage:      {risk_pct:.1f}%")

if risk_pct > 30:
    print("ALERT: High stock-out risk detected (>30%)")
elif risk_pct > 15:
    print("NOTICE: Moderate stock-out risk detected (>15%)")

# --- STEP 7: PRODUCT-LEVEL RISK ANALYSIS ---
print("\n[7/11] STOCK RISK BY PRODUCT (TOP 5)")
product_risk = master.groupby('SKU').agg({
    'Stock_Risk': ['sum', 'count', 'mean']
})
product_risk.columns = ['Risk_Transactions', 'Total_Transactions', 'Risk_Rate']
product_risk['Risk_Rate'] = product_risk['Risk_Rate'] * 100
product_risk = product_risk.sort_values('Risk_Rate', ascending=False)

for sku, row in product_risk.head().iterrows():
    print(
        f"  {sku:.<15} {row['Risk_Rate']:>5.1f}% Risk ({int(row['Risk_Transactions'])}/{int(row['Total_Transactions'])})")

# --- STEP 8: INVENTORY HEALTH METRICS ---
print("\n[8/11] CALCULATING INVENTORY CUSHION")
master['Inventory_Cushion'] = master['Stock_On_Hand'] - master['Reorder_Point']
below_reorder = (master['Inventory_Cushion'] < 0).sum()
print(f"Transactions occurring BELOW reorder point: {below_reorder} ({below_reorder / len(master) * 100:.1f}%)")

# --- STEP 9: DATA QUALITY VALIDATION ---
print("\n[9/11] FINAL QUALITY CHECK")
print(f"Duplicates:      {master.duplicated().sum()}")
print(f"Negative Rev:    {(master['Revenue'] < 0).sum()}")
print(f"Negative Units:  {(master['Units_Sold'] < 0).sum()}")
print(f"Date Coverage:   {master['Date'].min().date()} to {master['Date'].max().date()}")

# --- STEP 10: EXPORT MASTER DATASET ---
print("\n[10/11] EXPORTING DATA")
master.to_csv('../data/master_dataset.csv', index=False)
print(f"File saved to: ../data/master_dataset.csv ({len(master):,} rows)")

# --- STEP 11: SUMMARY INSIGHTS ---
print("\n[11/11] KEY TAKEAWAYS")
granola_rev_pct = (master[master['SKU'].str.contains('Granola')]['Revenue'].sum() / master['Revenue'].sum()) * 100

print(f"1. Stock Risk:    {risk_pct:.1f}% of volume affected")
print(f"2. Core Product:  Granola accounts for {granola_rev_pct:.1f}% of revenue")
print(f"3. Next Action:   Quantify specific revenue loss from stock-outs")

print("\n" + "-" * 70)
print("NOTEBOOK 02 PROCESSING COMPLETE")
print("-" * 70)