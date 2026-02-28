"""
NOTEBOOK 08: DEMAND FORECASTING & STOCK ALERT SYSTEM
=====================================================

Purpose:
1. Forecast next 30 days of demand
2. Calculate optimal reorder points
3. Create automated stock alert system

Business Value:
- Prevent stock-outs before they happen
- Optimize inventory levels
- Automated alerts for proactive management

Time: 40 minutes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings('ignore')

print("=" * 70)
print("NOTEBOOK 08: DEMAND FORECASTING & STOCK ALERT SYSTEM")
print("=" * 70)

# ============================================================================
# STEP 1: LOAD AND PREPARE DATA
# ============================================================================

print("\n[1/10] LOADING MASTER DATASET...")

master = pd.read_csv('../data/master_dataset.csv', parse_dates=['Date'])

print(f"Transactions loaded: {len(master):,}")
print(f"Date range: {master['Date'].min()} to {master['Date'].max()}")

# ============================================================================
# STEP 2: AGGREGATE TO DAILY LEVEL (CRITICAL!)
# ============================================================================

print("\n" + "=" * 70)
print("[2/10] AGGREGATING TO DAILY LEVEL")
print("=" * 70)

print("\nWHY DAILY AGGREGATION?")
print("-" * 70)
print("Problem: Transaction-level is too granular")
print("  Transaction 1: 50 units")
print("  Transaction 2: 30 units")
print("  Transaction 3: 40 units")
print()
print("What we need: Total daily demand")
print("  Day 1: 120 units total")
print()
print("This is what inventory decisions are based on!")
print("-" * 70)

# Aggregate by product
daily_by_product = master.groupby(['Date', 'SKU']).agg({
    'Units_Sold': 'sum',
    'Revenue': 'sum'
}).reset_index()

print(f"\nDaily data created: {len(daily_by_product):,} records")
print(f"Products tracked: {daily_by_product['SKU'].nunique()}")

# ============================================================================
# STEP 3: FOCUS ON GRANOLA PRODUCTS (HIGHEST PRIORITY)
# ============================================================================

print("\n" + "=" * 70)
print("[3/10] FOCUSING ON GRANOLA PRODUCTS")
print("=" * 70)

print("\nWHY GRANOLA?")
print("  - 52% of total revenue (most important)")
print("  - 22% stock-out risk (highest risk)")
print("  - $9,233 monthly recovery potential")

granola_data = daily_by_product[daily_by_product['SKU'].str.contains('Granola')]

print(f"\nGranola transactions: {len(granola_data)}")
print(f"Products: {granola_data['SKU'].unique()}")

# Combine both Granola products for overall demand
daily_granola = granola_data.groupby('Date').agg({
    'Units_Sold': 'sum',
    'Revenue': 'sum'
}).reset_index()

print(f"\nDaily Granola demand summary:")
print(f"  Average: {daily_granola['Units_Sold'].mean():.0f} units/day")
print(f"  Min: {daily_granola['Units_Sold'].min():.0f} units/day")
print(f"  Max: {daily_granola['Units_Sold'].max():.0f} units/day")
print(f"  Std Dev: {daily_granola['Units_Sold'].std():.0f} units/day")

# ============================================================================
# STEP 4: CREATE TIME SERIES FEATURES
# ============================================================================

print("\n" + "=" * 70)
print("[4/10] ENGINEERING TIME SERIES FEATURES")
print("=" * 70)

# Add temporal features
daily_granola['DayOfWeek'] = daily_granola['Date'].dt.dayofweek
daily_granola['Day'] = daily_granola['Date'].dt.day
daily_granola['Week'] = daily_granola['Date'].dt.isocalendar().week
daily_granola['Is_Weekend'] = daily_granola['DayOfWeek'].isin([5, 6]).astype(int)

# Lag features (yesterday affects today)
daily_granola['Lag_1'] = daily_granola['Units_Sold'].shift(1)
daily_granola['Lag_2'] = daily_granola['Units_Sold'].shift(2)
daily_granola['Lag_7'] = daily_granola['Units_Sold'].shift(7)  # Same day last week

# Rolling averages (trend)
daily_granola['MA_3'] = daily_granola['Units_Sold'].rolling(3).mean()
daily_granola['MA_7'] = daily_granola['Units_Sold'].rolling(7).mean()

# Remove NaN from lag features
daily_granola_clean = daily_granola.dropna()

print(f"Features created:")
print(f"  Temporal: DayOfWeek, Day, Week, Is_Weekend")
print(f"  Lag: Lag_1, Lag_2, Lag_7")
print(f"  Rolling: MA_3, MA_7")

print(f"\nData after feature engineering: {len(daily_granola_clean)} days")

# ============================================================================
# STEP 5: TRAIN-TEST SPLIT
# ============================================================================

print("\n" + "=" * 70)
print("[5/10] SPLITTING DATA FOR VALIDATION")
print("=" * 70)

# Use last 7 days as test (simulate forecasting next week)
train_size = len(daily_granola_clean) - 7
train = daily_granola_clean.iloc[:train_size]
test = daily_granola_clean.iloc[train_size:]

print(f"Training set: {train['Date'].min()} to {train['Date'].max()}")
print(f"  Size: {len(train)} days")
print(f"  Avg daily demand: {train['Units_Sold'].mean():.0f} units")

print(f"\nTest set: {test['Date'].min()} to {test['Date'].max()}")
print(f"  Size: {len(test)} days")
print(f"  Avg daily demand: {test['Units_Sold'].mean():.0f} units")

# ============================================================================
# STEP 6: TRAIN FORECASTING MODEL
# ============================================================================

print("\n" + "=" * 70)
print("[6/10] TRAINING RANDOM FOREST MODEL")
print("=" * 70)

feature_cols = ['DayOfWeek', 'Day', 'Week', 'Is_Weekend',
                'Lag_1', 'Lag_2', 'Lag_7', 'MA_3', 'MA_7']

X_train = train[feature_cols]
y_train = train['Units_Sold']

X_test = test[feature_cols]
y_test = test['Units_Sold']

# Train model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)

model.fit(X_train, y_train)
print("Model trained successfully")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nTop 5 most important features:")
print(feature_importance.head())

# ============================================================================
# STEP 7: VALIDATE MODEL
# ============================================================================

print("\n" + "=" * 70)
print("[7/10] MODEL VALIDATION")
print("=" * 70)

y_pred_test = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
r2 = r2_score(y_test, y_pred_test)
mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

print(f"Model Performance Metrics:")
print(f"  MAE:  {mae:.1f} units/day")
print(f"  RMSE: {rmse:.1f} units/day")
print(f"  R2:   {r2:.3f}")
print(f"  MAPE: {mape:.1f}%")

print(f"\nContext:")
print(f"  Average daily demand: {train['Units_Sold'].mean():.0f} units")
print(f"  Error as % of mean: {(mae / train['Units_Sold'].mean()) * 100:.1f}%")

if mape < 15:
    print("\nRESULT: Excellent forecast accuracy (< 15% MAPE)")
elif mape < 25:
    print("\nRESULT: Good forecast accuracy (15-25% MAPE)")
else:
    print("\nRESULT: Acceptable forecast accuracy")

# Visualization: Actual vs Predicted
plt.figure(figsize=(12, 6))
plt.plot(test['Date'], y_test, 'o-', linewidth=2, markersize=8,
         label='Actual', color='blue')
plt.plot(test['Date'], y_pred_test, 's-', linewidth=2, markersize=8,
         label='Predicted', color='red')
plt.fill_between(test['Date'], y_test, y_pred_test, alpha=0.2)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Units Sold', fontsize=12)
plt.title('Forecast Validation: Actual vs Predicted', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../outputs/forecast_validation.png', dpi=300, bbox_inches='tight')
print("\nSaved: forecast_validation.png")

# ============================================================================
# STEP 8: GENERATE 30-DAY FORECAST
# ============================================================================

print("\n" + "=" * 70)
print("[8/10] GENERATING 30-DAY FORECAST")
print("=" * 70)

# Start from last known date
last_date = daily_granola_clean['Date'].max()
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)

# Initialize with last known values
forecast_values = []
last_units = daily_granola_clean['Units_Sold'].iloc[-1]
last_7_values = daily_granola_clean['Units_Sold'].iloc[-7:].values.tolist()
last_3_values = daily_granola_clean['Units_Sold'].iloc[-3:].values.tolist()

for i, date in enumerate(forecast_dates):
    # Create features for this future date
    features = {
        'DayOfWeek': date.dayofweek,
        'Day': date.day,
        'Week': date.isocalendar()[1],
        'Is_Weekend': 1 if date.dayofweek in [5, 6] else 0,
        'Lag_1': last_units,
        'Lag_2': last_3_values[-2] if len(last_3_values) >= 2 else last_units,
        'Lag_7': last_7_values[0] if i < 7 else forecast_values[i - 7],
        'MA_3': np.mean(last_3_values[-3:]),
        'MA_7': np.mean(last_7_values[-7:])
    }

    # Predict
    pred = model.predict(pd.DataFrame([features]))[0]
    forecast_values.append(pred)

    # Update for next iteration
    last_units = pred
    last_3_values = last_3_values[1:] + [pred]
    if i < 7:
        last_7_values = last_7_values[1:] + [pred]
    else:
        last_7_values = [forecast_values[i - 6 + j] for j in range(7)]

# Create forecast dataframe
forecast_df = pd.DataFrame({
    'Date': forecast_dates,
    'Predicted_Units': forecast_values
})

print(f"\n30-Day Forecast Summary:")
print(f"  Total units: {sum(forecast_values):.0f}")
print(f"  Average daily: {np.mean(forecast_values):.0f}")
print(f"  Min daily: {min(forecast_values):.0f}")
print(f"  Max daily: {max(forecast_values):.0f}")

# Save forecast
forecast_df.to_csv('../outputs/demand_forecast_30days.csv', index=False)
print("\nSaved: demand_forecast_30days.csv")

# Visualization
fig, ax = plt.subplots(figsize=(14, 6))

# Historical data (last 15 days)
historical = daily_granola_clean.iloc[-15:]
ax.plot(historical['Date'], historical['Units_Sold'],
        'o-', linewidth=2, label='Historical', color='blue')

# Forecast
ax.plot(forecast_df['Date'], forecast_df['Predicted_Units'],
        's--', linewidth=2, label='Forecast', color='red')

# Confidence band (±1 std)
forecast_std = np.std(forecast_values)
ax.fill_between(forecast_df['Date'],
                forecast_df['Predicted_Units'] - forecast_std,
                forecast_df['Predicted_Units'] + forecast_std,
                alpha=0.2, color='red', label='Confidence Band')

ax.axvline(x=last_date, color='black', linestyle='--',
           linewidth=2, label='Forecast Start')

ax.set_title('30-Day Demand Forecast: Granola Products',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Daily Units Sold')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('../outputs/forecast_30days.png', dpi=300, bbox_inches='tight')
print("Saved: forecast_30days.png")

# ============================================================================
# STEP 9: CALCULATE OPTIMAL REORDER POINTS
# ============================================================================

print("\n" + "=" * 70)
print("[9/10] CALCULATING OPTIMAL REORDER POINTS")
print("=" * 70)

print("\nSAFETY STOCK FORMULA:")
print("-" * 70)
print("Safety Stock = Z-score × StdDev(Daily_Demand) × √(Lead_Time)")
print()
print("Where:")
print("  Z-score: 1.65 for 95% service level")
print("  StdDev: Variability in daily demand")
print("  Lead_Time: Days until restock arrives")
print()
print("Reorder Point = (Avg_Daily_Demand × Lead_Time) + Safety_Stock")
print("-" * 70)

# Parameters
avg_daily_demand = np.mean(forecast_values)
std_daily_demand = np.std(forecast_values)
lead_time = 6  # days (from inventory data)
service_level = 0.95
z_score = 1.65  # for 95% service level

safety_stock = z_score * std_daily_demand * np.sqrt(lead_time)
reorder_point = (avg_daily_demand * lead_time) + safety_stock

print(f"\nInputs:")
print(f"  Avg daily demand: {avg_daily_demand:.0f} units")
print(f"  Std deviation: {std_daily_demand:.0f} units")
print(f"  Lead time: {lead_time} days")
print(f"  Service level: {service_level * 100:.0f}%")

print(f"\nResults:")
print(f"  Safety Stock: {safety_stock:.0f} units")
print(f"  Demand during lead time: {avg_daily_demand * lead_time:.0f} units")
print(f"  RECOMMENDED REORDER POINT: {reorder_point:.0f} units")

# Compare to current
inventory = pd.read_csv('../data/inventory_data.csv')
current_reorder = inventory[inventory['SKU'].str.contains('Granola')]['Reorder_Point'].mean()

print(f"\nComparison:")
print(f"  Current reorder point: {current_reorder:.0f} units")
print(f"  Recommended: {reorder_point:.0f} units")
print(
    f"  Increase needed: {reorder_point - current_reorder:.0f} units ({((reorder_point / current_reorder - 1) * 100):.0f}% increase)")

# ============================================================================
# STEP 10: STOCK ALERT SYSTEM
# ============================================================================

print("\n" + "=" * 70)
print("[10/10] AUTOMATED STOCK ALERT SYSTEM")
print("=" * 70)

print("\nALERT SYSTEM DESIGN:")
print("-" * 70)
print("3-Tier Alert System:")
print()
print("GREEN (Healthy):  Stock > Reorder Point + Buffer")
print("YELLOW (Warning): Stock between Reorder Point and Buffer")
print("RED (Critical):   Stock <= Reorder Point")
print("-" * 70)

# Define thresholds
buffer = safety_stock * 0.5  # 50% of safety stock as buffer
yellow_threshold = reorder_point + buffer
red_threshold = reorder_point

print(f"\nAlert Thresholds:")
print(f"  RED (Critical):    <= {red_threshold:.0f} units")
print(f"  YELLOW (Warning):  {red_threshold:.0f} - {yellow_threshold:.0f} units")
print(f"  GREEN (Healthy):   > {yellow_threshold:.0f} units")


# Create alert function
def generate_stock_alert(current_stock, product_name):
    """
    Generate stock alert based on current inventory level
    """
    if current_stock <= red_threshold:
        status = "RED - CRITICAL"
        action = "ORDER IMMEDIATELY"
        urgency = "HIGH"
        message = f"URGENT: {product_name} at CRITICAL level ({current_stock:.0f} units). Reorder NOW!"
    elif current_stock <= yellow_threshold:
        status = "YELLOW - WARNING"
        action = "Schedule order within 24-48 hours"
        urgency = "MEDIUM"
        message = f"Warning: {product_name} approaching reorder point ({current_stock:.0f} units). Plan restock."
    else:
        status = "GREEN - HEALTHY"
        action = "No action needed"
        urgency = "LOW"
        message = f"OK: {product_name} stock level healthy ({current_stock:.0f} units)."

    return {
        'Product': product_name,
        'Current_Stock': current_stock,
        'Status': status,
        'Urgency': urgency,
        'Action': action,
        'Message': message,
        'Reorder_Point': red_threshold,
        'Days_Until_Stockout': int(current_stock / avg_daily_demand) if current_stock > 0 else 0
    }


# Test with different stock levels
print("\n" + "=" * 70)
print("ALERT SYSTEM SIMULATION")
print("=" * 70)

test_scenarios = [
    (50, "Granola_Nut"),
    (150, "Granola_Honey"),
    (300, "Granola_Nut"),
]

alerts = []
for stock_level, product in test_scenarios:
    alert = generate_stock_alert(stock_level, product)
    alerts.append(alert)

    print(f"\nScenario: {product} with {stock_level} units")
    print(f"  Status: {alert['Status']}")
    print(f"  Days until stockout: {alert['Days_Until_Stockout']}")
    print(f"  Action: {alert['Action']}")
    print(f"  Message: {alert['Message']}")

# Save alert system configuration
alert_config = pd.DataFrame([{
    'Product_Category': 'Granola',
    'Avg_Daily_Demand': avg_daily_demand,
    'Lead_Time_Days': lead_time,
    'Safety_Stock': safety_stock,
    'Reorder_Point': reorder_point,
    'Yellow_Threshold': yellow_threshold,
    'Red_Threshold': red_threshold,
    'Service_Level': service_level,
    'Last_Updated': pd.Timestamp.now()
}])

alert_config.to_csv('../outputs/stock_alert_config.csv', index=False)
print("\nSaved: stock_alert_config.csv")

# Save recommendations
recommendations = pd.DataFrame([{
    'Product': 'Granola Products',
    'Current_Reorder_Point': current_reorder,
    'Recommended_Reorder_Point': reorder_point,
    'Increase_Needed': reorder_point - current_reorder,
    'Safety_Stock': safety_stock,
    'Expected_Daily_Demand': avg_daily_demand,
    'Lead_Time_Days': lead_time,
    'Service_Level_Target': service_level
}])

recommendations.to_csv('../outputs/inventory_recommendations.csv', index=False)
print("Saved: inventory_recommendations.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PROJECT COMPLETE - DEMAND FORECASTING & ALERTS")
print("=" * 70)

print(f"""
FORECAST RESULTS:
-----------------
30-Day Forecast:     {sum(forecast_values):.0f} total units
Daily Average:       {np.mean(forecast_values):.0f} units
Model Accuracy:      {100 - mape:.1f}% (MAPE: {mape:.1f}%)

INVENTORY RECOMMENDATIONS:
--------------------------
Current Reorder Point:    {current_reorder:.0f} units
Recommended:              {reorder_point:.0f} units
Increase Needed:          {reorder_point - current_reorder:.0f} units ({((reorder_point / current_reorder - 1) * 100):.0f}%)

Safety Stock Buffer:      {safety_stock:.0f} units
Service Level Target:     {service_level * 100:.0f}%

ALERT SYSTEM:
-------------
RED Alert:     <= {red_threshold:.0f} units (Order immediately!)
YELLOW Alert:  {red_threshold:.0f}-{yellow_threshold:.0f} units (Plan restock)
GREEN Status:  > {yellow_threshold:.0f} units (Healthy)

BUSINESS IMPACT:
----------------
If implemented:
- Prevents stock-outs through proactive alerts
- Maintains 95% service level
- Reduces emergency shipments
- Expected recovery: $9,059/month (stock-out reduction)

DELIVERABLES:
-------------
1. demand_forecast_30days.csv (30-day forecast)
2. forecast_validation.png (model accuracy proof)
3. forecast_30days.png (visual forecast)
4. stock_alert_config.csv (alert thresholds)
5. inventory_recommendations.csv (action items)

NEXT STEPS:
-----------
1. Implement alert system in inventory management software
2. Update reorder points to recommended levels
3. Monitor forecast accuracy weekly
4. Adjust safety stock if service level deviates
""")

print("=" * 70)
print("NOTEBOOK 07 COMPLETE")
print("=" * 70)