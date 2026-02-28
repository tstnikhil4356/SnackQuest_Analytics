"""
Notebook 1: Initial Data Exploration
------------------------------------
Objective: Load datasets, validate structure, and calculate baseline metrics.
"""

import pandas as pd
import numpy as np

# --- Configuration & Loading ---
print("-" * 50)
print("SNACKQUEST DATA ANALYSIS: INITIAL EXPLORATION")
print("-" * 50)

try:
    sales = pd.read_csv('../data/sales_data.csv')
    inventory = pd.read_csv('../data/inventory_data.csv')
    customers = pd.read_csv('../data/customer_data.csv')
    print("Data successfully loaded from /data/")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")

# --- Sales Dataset Overview ---
print("\n[SALES DATA SUMMARY]")
print(f"Total Records: {len(sales):,}")
print(f"Timeframe:     {sales['Date'].min()} to {sales['Date'].max()}")
print(f"Columns:       {', '.join(sales.columns)}")

print("\nSample Data (First 3 rows):")
print(sales.head(3))

print("\nMissing Value Counts:")
print(sales.isnull().sum())

# --- Promotion Analysis ---
print("\n[PROMOTION DISTRIBUTION]")
print(sales['Promotion'].value_counts())

# --- Revenue Calculations ---
sales['Revenue'] = sales['Price'] * sales['Units_Sold']
total_rev = sales['Revenue'].sum()
total_units = sales['Units_Sold'].sum()

print(f"\nTotal Revenue: ${total_rev:,.2f}")
print(f"Total Units:   {total_units:,}")

# --- Category Breakdown ---
print("\n[REVENUE BY CATEGORY]")
cat_revenue = sales.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
for cat, rev in cat_revenue.items():
    pct = (rev / total_rev) * 100
    print(f"  {cat:.<15} ${rev:,.0f} ({pct:.1f}%)")

# --- Top Product Performance ---
print("\n[TOP 5 PRODUCTS BY REVENUE]")
prod_revenue = sales.groupby('SKU')['Revenue'].sum().sort_values(ascending=False).head(5)
for i, (sku, rev) in enumerate(prod_revenue.items(), 1):
    pct = (rev / total_rev) * 100
    print(f"  {i}. {sku:.<12} ${rev:,.0f} ({pct:.1f}%)")

# --- Inventory & Customer Metadata ---
print("\n[METADATA CHECKS]")
print(f"Inventory: {len(inventory)} unique store-SKU mappings")
print(f"Customers: {len(customers)} registered profiles")
print(f"Avg Spend: ${customers['Avg_Monthly_Spend'].mean():.2f}")
print(f"Avg Tenue: {customers['Loyalty_Years'].mean():.1f} years")

# --- Export ---
sales.to_csv('../data/sales_with_revenue.csv', index=False)
print("\nProcessing complete. Exported: sales_with_revenue.csv")