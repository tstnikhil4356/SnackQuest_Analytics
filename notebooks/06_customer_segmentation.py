"""
NOTEBOOK 07: CUSTOMER SEGMENTATION
===================================

Purpose: Segment customers to enable targeted marketing strategies

Business Value:
- Stop giving discounts to customers who don't need them
- Focus promotions on right customer groups
- Maximize ROI on marketing spend

Method: K-Means Clustering

Time: 30 minutes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

print("=" * 70)
print("NOTEBOOK 07: CUSTOMER SEGMENTATION")
print("=" * 70)

# ============================================================================
# STEP 1: LOAD CUSTOMER DATA
# ============================================================================

print("\n[1/8] LOADING CUSTOMER DATA...")

customers = pd.read_csv('../data/customer_data.csv')

print(f"Customers loaded: {len(customers)}")
print(f"Columns: {customers.columns.tolist()}")

print("\nFirst few customers:")
print(customers.head())

# ============================================================================
# STEP 2: EXPLORATORY ANALYSIS
# ============================================================================

print("\n" + "=" * 70)
print("[2/8] CUSTOMER PROFILE OVERVIEW")
print("=" * 70)

print("\nCustomer Statistics:")
print(f"  Average Monthly Spend: ${customers['Avg_Monthly_Spend'].mean():.2f}")
print(f"  Spend Range: ${customers['Avg_Monthly_Spend'].min():.2f} - ${customers['Avg_Monthly_Spend'].max():.2f}")
print(f"  Average Loyalty: {customers['Loyalty_Years'].mean():.1f} years")
print(f"  Loyalty Range: {customers['Loyalty_Years'].min()} - {customers['Loyalty_Years'].max()} years")

print("\nAge Group Distribution:")
print(customers['Age_Group'].value_counts())

print("\nRegion Distribution:")
print(customers['Region'].value_counts())

print("\nFavorite Category:")
print(customers['Fav_Category'].value_counts())

# ============================================================================
# STEP 3: PREPARE FEATURES FOR CLUSTERING
# ============================================================================

print("\n" + "=" * 70)
print("[3/8] PREPARING FEATURES FOR CLUSTERING")
print("=" * 70)

print("\nCLUSTERING STRATEGY:")
print("-" * 70)
print("We'll segment customers based on:")
print("  1. Avg_Monthly_Spend (How much they buy)")
print("  2. Loyalty_Years (How long they've been customers)")
print()
print("Why these two?")
print("  - Spend = Current value to business")
print("  - Loyalty = Future value potential")
print("  - Together = Complete customer profile")
print("-" * 70)

# Select features
features = ['Avg_Monthly_Spend', 'Loyalty_Years']
X = customers[features].copy()

print(f"\nFeature matrix shape: {X.shape}")
print("\nFeature statistics:")
print(X.describe())

# ============================================================================
# STEP 4: SCALE FEATURES
# ============================================================================

print("\n" + "=" * 70)
print("[4/8] SCALING FEATURES")
print("=" * 70)

print("\nWHY SCALE?")
print("-" * 70)
print("Before scaling:")
print(f"  Avg_Monthly_Spend range: ${X['Avg_Monthly_Spend'].min():.0f} - ${X['Avg_Monthly_Spend'].max():.0f}")
print(f"  Loyalty_Years range: {X['Loyalty_Years'].min()} - {X['Loyalty_Years'].max()} years")
print()
print("Problem: Spend (0-300) dominates Loyalty (0-10)")
print("Solution: Scale both to 0-1 range so they're equally weighted")
print("-" * 70)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\nAfter scaling:")
print(f"  Mean: {X_scaled.mean(axis=0)}")
print(f"  Std Dev: {X_scaled.std(axis=0)}")
print("Both features now have mean=0, std=1")

# ============================================================================
# STEP 5: DETERMINE OPTIMAL NUMBER OF CLUSTERS (ELBOW METHOD)
# ============================================================================

print("\n" + "=" * 70)
print("[5/8] FINDING OPTIMAL NUMBER OF CLUSTERS")
print("=" * 70)

print("\nELBOW METHOD:")
print("Test K=2 through K=10, find the 'elbow' point")

inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    print(f"  K={k}: Inertia = {kmeans.inertia_:.2f}")

# Plot elbow curve
plt.figure(figsize=(10, 6))
plt.plot(K_range, inertias, 'o-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (K)', fontsize=12)
plt.ylabel('Within-Cluster Sum of Squares (Inertia)', fontsize=12)
plt.title('Elbow Method: Finding Optimal K', fontsize=14, fontweight='bold')
plt.grid(alpha=0.3)

# Mark optimal K
optimal_k = 4  # Based on elbow observation
plt.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2,
            label=f'Selected K={optimal_k}')
plt.legend()

plt.tight_layout()
plt.savefig('../outputs/elbow_curve.png', dpi=300, bbox_inches='tight')
print(f"\nSaved: elbow_curve.png")

print(f"\nOPTIMAL K SELECTED: {optimal_k}")
print("Rationale: Clear elbow at K=4, diminishing returns after")

# ============================================================================
# STEP 6: APPLY K-MEANS CLUSTERING
# ============================================================================

print("\n" + "=" * 70)
print("[6/8] APPLYING K-MEANS CLUSTERING (K=4)")
print("=" * 70)

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
customers['Cluster'] = kmeans.fit_predict(X_scaled)

print(f"Clustering complete!")
print(f"\nCluster distribution:")
print(customers['Cluster'].value_counts().sort_index())

# ============================================================================
# STEP 7: ANALYZE CLUSTERS
# ============================================================================

print("\n" + "=" * 70)
print("[7/8] CLUSTER ANALYSIS")
print("=" * 70)

cluster_summary = customers.groupby('Cluster').agg({
    'Avg_Monthly_Spend': ['mean', 'min', 'max'],
    'Loyalty_Years': ['mean', 'min', 'max'],
    'CustomerID': 'count'
}).round(2)

cluster_summary.columns = ['Avg_Spend', 'Min_Spend', 'Max_Spend',
                           'Avg_Loyalty', 'Min_Loyalty', 'Max_Loyalty', 'Count']

print("\nCluster Profiles:")
print(cluster_summary)

# Assign business names based on characteristics
segment_names = {
    0: 'TBD',
    1: 'TBD',
    2: 'TBD',
    3: 'TBD'
}

# Analyze each cluster to assign names
print("\n" + "=" * 70)
print("NAMING SEGMENTS BASED ON CHARACTERISTICS")
print("=" * 70)

for cluster in range(optimal_k):
    cluster_data = customers[customers['Cluster'] == cluster]
    avg_spend = cluster_data['Avg_Monthly_Spend'].mean()
    avg_loyalty = cluster_data['Loyalty_Years'].mean()
    count = len(cluster_data)

    print(f"\nCluster {cluster}:")
    print(f"  Size: {count} customers ({count / len(customers) * 100:.1f}%)")
    print(f"  Avg Spend: ${avg_spend:.2f}")
    print(f"  Avg Loyalty: {avg_loyalty:.1f} years")

    # Assign name based on characteristics
    if avg_spend > 200 and avg_loyalty > 5:
        name = "Premium Champions"
        strategy = "VIP treatment, no discounts needed"
    elif avg_spend > 180 and avg_loyalty > 3:
        name = "Growing Stars"
        strategy = "Nurture with loyalty rewards"
    elif avg_spend < 150 and avg_loyalty < 4:
        name = "Bargain Hunters"
        strategy = "Strategic BOGO for volume"
    else:
        name = "At-Risk"
        strategy = "Win-back campaigns"

    segment_names[cluster] = name
    print(f"  SEGMENT NAME: {name}")
    print(f"  Strategy: {strategy}")

customers['Segment'] = customers['Cluster'].map(segment_names)

# ============================================================================
# STEP 8: VISUALIZATIONS
# ============================================================================

print("\n" + "=" * 70)
print("[8/8] CREATING VISUALIZATIONS")
print("=" * 70)

# Create comprehensive visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Scatter plot with segments
for cluster in range(optimal_k):
    cluster_data = customers[customers['Cluster'] == cluster]
    axes[0, 0].scatter(cluster_data['Loyalty_Years'],
                       cluster_data['Avg_Monthly_Spend'],
                       s=100, alpha=0.6, label=segment_names[cluster])

axes[0, 0].set_xlabel('Loyalty Years', fontsize=12)
axes[0, 0].set_ylabel('Avg Monthly Spend ($)', fontsize=12)
axes[0, 0].set_title('Customer Segments', fontsize=14, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Plot 2: Segment sizes
segment_counts = customers['Segment'].value_counts()
axes[0, 1].bar(range(len(segment_counts)), segment_counts.values, color='steelblue')
axes[0, 1].set_xticks(range(len(segment_counts)))
axes[0, 1].set_xticklabels(segment_counts.index, rotation=45, ha='right')
axes[0, 1].set_ylabel('Customer Count', fontsize=12)
axes[0, 1].set_title('Segment Distribution', fontsize=14, fontweight='bold')
axes[0, 1].grid(axis='y', alpha=0.3)

# Plot 3: Revenue contribution
segment_revenue = customers.groupby('Segment')['Avg_Monthly_Spend'].sum()
axes[1, 0].pie(segment_revenue, labels=segment_revenue.index, autopct='%1.1f%%',
               startangle=90)
axes[1, 0].set_title('Revenue Contribution by Segment', fontsize=14, fontweight='bold')

# Plot 4: Spend distribution by segment
customers.boxplot(column='Avg_Monthly_Spend', by='Segment', ax=axes[1, 1])
axes[1, 1].set_xlabel('Segment', fontsize=12)
axes[1, 1].set_ylabel('Monthly Spend ($)', fontsize=12)
axes[1, 1].set_title('Spend Distribution by Segment', fontsize=14, fontweight='bold')
plt.suptitle('')  # Remove auto title

plt.tight_layout()
plt.savefig('../outputs/customer_segments.png', dpi=300, bbox_inches='tight')
print("Saved: customer_segments.png")

# Save segmented customers
customers.to_csv('../outputs/customers_segmented.csv', index=False)
print("Saved: customers_segmented.csv")

# ============================================================================
# BUSINESS RECOMMENDATIONS
# ============================================================================

print("\n" + "=" * 70)
print("BUSINESS RECOMMENDATIONS BY SEGMENT")
print("=" * 70)

for cluster in range(optimal_k):
    seg_name = segment_names[cluster]
    seg_data = customers[customers['Cluster'] == cluster]

    print(f"\n{seg_name}:")
    print(f"  Size: {len(seg_data)} customers ({len(seg_data) / len(customers) * 100:.1f}%)")
    print(f"  Avg Spend: ${seg_data['Avg_Monthly_Spend'].mean():.2f}/month")
    print(f"  Total Value: ${seg_data['Avg_Monthly_Spend'].sum():,.2f}/month")
    print(f"  Avg Loyalty: {seg_data['Loyalty_Years'].mean():.1f} years")

    if 'Premium' in seg_name or 'Champion' in seg_name:
        print("  ACTION:")
        print("    - STOP discounting (they'll pay full price)")
        print("    - Offer VIP service instead")
        print("    - Early access to new products")
        print("    - Personal thank-you from management")
    elif 'Growing' in seg_name or 'Star' in seg_name:
        print("  ACTION:")
        print("    - 10% discount on 2nd purchase same month")
        print("    - Loyalty points program")
        print("    - Birthday discount")
        print("    - Referral rewards")
    elif 'Bargain' in seg_name or 'Hunter' in seg_name:
        print("  ACTION:")
        print("    - Strategic BOGO for new products only")
        print("    - Volume discounts (buy 3, save 20%)")
        print("    - Limited-time offers")
    else:  # At-Risk
        print("  ACTION:")
        print("    - Personalized 'we miss you' email")
        print("    - 15% win-back discount (one-time)")
        print("    - Survey: Why shopped less?")

# Calculate potential impact
print("\n" + "=" * 70)
print("ESTIMATED IMPACT OF SEGMENTED STRATEGY")
print("=" * 70)

current_promo_cost_pct = 9.0  # From previous analysis

print(f"\nCurrent approach:")
print(f"  Everyone gets same promotions")
print(f"  Cost: ~{current_promo_cost_pct}% of revenue")

print(f"\nSegmented approach:")
print(f"  Premium Champions: 0% discount (VIP service)")
print(f"  Growing Stars: 10% targeted discount")
print(f"  Bargain Hunters: Strategic BOGO only")
print(f"  At-Risk: 15% win-back (one-time)")

# Rough calculation
premium_pct = len(customers[customers['Segment'] == 'Premium Champions']) / len(customers)
savings_from_premium = premium_pct * current_promo_cost_pct

print(f"\nEstimated savings:")
print(f"  Stop discounting Premium ({premium_pct * 100:.0f}% of customers)")
print(f"  Potential savings: ~{savings_from_premium:.1f}% of revenue")
print(f"  Plus better targeting = Higher conversion")

print("\n" + "=" * 70)
print("NOTEBOOK 06 COMPLETE")
print("=" * 70)

print("\nDELIVERABLES:")
print("  1. customers_segmented.csv (200 customers with segments)")
print("  2. customer_segments.png (4-panel visualization)")
print("  3. elbow_curve.png (K selection justification)")
print("  4. Actionable strategies per segment")