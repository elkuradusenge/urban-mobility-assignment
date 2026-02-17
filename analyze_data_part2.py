import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

ANALYSIS_DIR = "analysis_results"

print("=" * 80)
print("NYC TAXI DATA ANALYSIS - PART 2: ECONOMIC & OPERATIONAL METRICS")
print("=" * 80)
print(f"Analysis Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load data
print("Loading data...")
DATA_FILE = "new-clean-dataset/clean_tripdata.parquet"
df = pd.read_parquet(DATA_FILE, engine='pyarrow')

# Convert datetime columns
df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

print(f"Loaded {len(df):,} records\n")

# Load previous results
with open(f"{ANALYSIS_DIR}/analysis_results_part1.json", 'r') as f:
    analysis_results = json.load(f)

print("=" * 80)
print("3. ECONOMIC ANALYSIS")
print("=" * 80)

# 3.1 Fare analysis
print("\n3.1 Fare Analysis")
print("-" * 80)

fare_stats = df['fare_amount'].describe()
print(f"Fare Statistics:")
print(f"  Mean:      ${fare_stats['mean']:.2f}")
print(f"  Median:    ${df['fare_amount'].median():.2f}")
print(f"  Std Dev:   ${fare_stats['std']:.2f}")
print(f"  Min:       ${fare_stats['min']:.2f}")
print(f"  Max:       ${fare_stats['max']:.2f}")
print(f"  25th %ile: ${fare_stats['25%']:.2f}")
print(f"  75th %ile: ${fare_stats['75%']:.2f}")

analysis_results["economic_analysis"] = {
    "fare": {
        "mean": float(fare_stats['mean']),
        "median": float(df['fare_amount'].median()),
        "std": float(fare_stats['std']),
        "min": float(fare_stats['min']),
        "max": float(fare_stats['max'])
    }
}

# Total revenue
total_revenue = df['total_amount'].sum()
print(f"\nTotal Revenue (January 2019): ${total_revenue:,.2f} (${total_revenue/1e6:.2f}M)")
analysis_results["economic_analysis"]["total_revenue"] = float(total_revenue)

# Plot fare distribution
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Histogram
axes[0].hist(df['fare_amount'], bins=50, color='green', alpha=0.7, edgecolor='black')
axes[0].set_xlabel('Fare Amount ($)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Fare Amount Distribution')
axes[0].axvline(fare_stats['mean'], color='red', linestyle='--', label=f'Mean: ${fare_stats["mean"]:.2f}')
axes[0].axvline(df['fare_amount'].median(), color='blue', linestyle='--', label=f'Median: ${df["fare_amount"].median():.2f}')
axes[0].legend()
axes[0].set_xlim(0, 100)
axes[0].grid(alpha=0.3)

# Box plot
axes[1].boxplot([df[df['fare_amount'] < 100]['fare_amount']], 
                labels=['Fare'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightgreen', alpha=0.7))
axes[1].set_ylabel('Fare Amount ($)')
axes[1].set_title('Fare Distribution (Box Plot)')
axes[1].grid(alpha=0.3)

# Fare by distance
fare_by_distance = df.groupby(pd.cut(df['trip_distance'], bins=20))['fare_amount'].mean()
axes[2].plot(range(len(fare_by_distance)), fare_by_distance.values, 
             marker='o', color='darkgreen', linewidth=2)
axes[2].set_xlabel('Distance Bin')
axes[2].set_ylabel('Average Fare ($)')
axes[2].set_title('Average Fare by Distance')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/06_fare_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 06_fare_analysis.png")

# 3.2 Tip analysis
print("\n3.2 Tip Analysis")
print("-" * 80)

tip_stats = df['tip_amount'].describe()
tip_pct_stats = df['tip_percentage'].describe()

print(f"Tip Amount Statistics:")
print(f"  Mean:      ${tip_stats['mean']:.2f}")
print(f"  Median:    ${df['tip_amount'].median():.2f}")
print(f"  Total:     ${df['tip_amount'].sum():,.2f}")

print(f"\nTip Percentage Statistics:")
print(f"  Mean:      {tip_pct_stats['mean']:.2f}%")
print(f"  Median:    {df['tip_percentage'].median():.2f}%")
print(f"  25th %ile: {tip_pct_stats['25%']:.2f}%")
print(f"  75th %ile: {tip_pct_stats['75%']:.2f}%")

# Analyze tipping behavior
no_tip = (df['tip_amount'] == 0).sum()
with_tip = (df['tip_amount'] > 0).sum()
generous_tip = (df['tip_percentage'] >= 20).sum()

print(f"\nTipping Behavior:")
print(f"  Trips with tip:    {with_tip:,} ({with_tip/len(df)*100:.1f}%)")
print(f"  Trips without tip: {no_tip:,} ({no_tip/len(df)*100:.1f}%)")
print(f"  Generous tips (≥20%): {generous_tip:,} ({generous_tip/len(df)*100:.1f}%)")

analysis_results["economic_analysis"]["tips"] = {
    "mean_amount": float(tip_stats['mean']),
    "mean_percentage": float(tip_pct_stats['mean']),
    "percentage_with_tip": float(with_tip/len(df)*100),
    "percentage_generous": float(generous_tip/len(df)*100)
}

# Plot tip analysis
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Tip amount distribution
axes[0, 0].hist(df[df['tip_amount'] < 20]['tip_amount'], bins=50, 
                color='gold', alpha=0.7, edgecolor='black')
axes[0, 0].set_xlabel('Tip Amount ($)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Tip Amount Distribution (< $20)')
axes[0, 0].grid(alpha=0.3)

# Tip percentage distribution
axes[0, 1].hist(df[df['tip_percentage'] < 50]['tip_percentage'], bins=50, 
                color='orange', alpha=0.7, edgecolor='black')
axes[0, 1].set_xlabel('Tip Percentage (%)')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Tip Percentage Distribution (< 50%)')
axes[0, 1].axvline(15, color='red', linestyle='--', label='Standard 15%')
axes[0, 1].axvline(20, color='green', linestyle='--', label='Generous 20%')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Tip by payment type
tip_by_payment = df.groupby('payment_type')['tip_percentage'].mean().sort_values(ascending=False).head(5)
axes[1, 0].bar(range(len(tip_by_payment)), tip_by_payment.values, color='purple', alpha=0.7)
axes[1, 0].set_xticks(range(len(tip_by_payment)))
axes[1, 0].set_xticklabels([f'Type {int(x)}' for x in tip_by_payment.index])
axes[1, 0].set_ylabel('Average Tip %')
axes[1, 0].set_title('Average Tip % by Payment Type')
axes[1, 0].grid(axis='y', alpha=0.3)

# Tipping behavior pie chart
tip_categories = ['No Tip', 'Standard (<20%)', 'Generous (≥20%)']
tip_counts = [
    no_tip,
    len(df[(df['tip_percentage'] > 0) & (df['tip_percentage'] < 20)]),
    generous_tip
]
axes[1, 1].pie(tip_counts, labels=tip_categories, autopct='%1.1f%%', 
               colors=['lightcoral', 'lightyellow', 'lightgreen'], startangle=90)
axes[1, 1].set_title('Tipping Behavior Distribution')

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/07_tip_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 07_tip_analysis.png")

# 3.3 Revenue breakdown
print("\n3.3 Revenue Component Analysis")
print("-" * 80)

revenue_components = {
    'Base Fare': df['fare_amount'].sum(),
    'Tips': df['tip_amount'].sum(),
    'Tolls': df['tolls_amount'].sum(),
    'MTA Tax': df['mta_tax'].sum(),
    'Extra': df['extra'].sum(),
    'Improvement Surcharge': df['improvement_surcharge'].sum(),
    'Congestion Surcharge': df['congestion_surcharge'].sum()
}

print("Revenue Components:")
for component, amount in revenue_components.items():
    pct = amount / total_revenue * 100
    print(f"  {component:<25} ${amount:>14,.2f}  ({pct:>5.2f}%)")

analysis_results["economic_analysis"]["revenue_breakdown"] = {k: float(v) for k, v in revenue_components.items()}

# Plot revenue breakdown
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].pie(revenue_components.values(), labels=revenue_components.keys(), 
            autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2"))
axes[0].set_title('Revenue Components Distribution')

# Bar chart
axes[1].barh(list(revenue_components.keys()), [v/1e6 for v in revenue_components.values()], 
             color='teal', alpha=0.7)
axes[1].set_xlabel('Revenue ($ Million)')
axes[1].set_title('Revenue Components Breakdown')
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/08_revenue_breakdown.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 08_revenue_breakdown.png")

print("\n✓ Economic analysis complete\n")

print("=" * 80)
print("4. OPERATIONAL ANALYSIS")
print("=" * 80)

# 4.1 Distance analysis
print("\n4.1 Trip Distance Analysis")
print("-" * 80)

distance_stats = df['trip_distance'].describe()
print(f"Distance Statistics (miles):")
print(f"  Mean:      {distance_stats['mean']:.2f}")
print(f"  Median:    {df['trip_distance'].median():.2f}")
print(f"  Std Dev:   {distance_stats['std']:.2f}")
print(f"  Min:       {distance_stats['min']:.2f}")
print(f"  Max:       {distance_stats['max']:.2f}")
print(f"  Total:     {df['trip_distance'].sum():,.0f} miles")

analysis_results["operational_analysis"] = {
    "distance": {
        "mean": float(distance_stats['mean']),
        "median": float(df['trip_distance'].median()),
        "std": float(distance_stats['std']),
        "total": float(df['trip_distance'].sum())
    }
}

# Distance categories
short_trips = (df['trip_distance'] < 2).sum()
medium_trips = ((df['trip_distance'] >= 2) & (df['trip_distance'] < 10)).sum()
long_trips = (df['trip_distance'] >= 10).sum()

print(f"\nDistance Categories:")
print(f"  Short (<2 mi):      {short_trips:,} ({short_trips/len(df)*100:.1f}%)")
print(f"  Medium (2-10 mi):   {medium_trips:,} ({medium_trips/len(df)*100:.1f}%)")
print(f"  Long (≥10 mi):      {long_trips:,} ({long_trips/len(df)*100:.1f}%)")

# 4.2 Duration analysis
print("\n4.2 Trip Duration Analysis")
print("-" * 80)

duration_stats = df['duration_min'].describe()
print(f"Duration Statistics (minutes):")
print(f"  Mean:      {duration_stats['mean']:.2f}")
print(f"  Median:    {df['duration_min'].median():.2f}")
print(f"  Std Dev:   {duration_stats['std']:.2f}")

analysis_results["operational_analysis"]["duration"] = {
    "mean": float(duration_stats['mean']),
    "median": float(df['duration_min'].median()),
    "std": float(duration_stats['std'])
}

# Duration categories
quick_trips = (df['duration_min'] < 10).sum()
normal_trips = ((df['duration_min'] >= 10) & (df['duration_min'] < 30)).sum()
long_duration = (df['duration_min'] >= 30).sum()

print(f"\nDuration Categories:")
print(f"  Quick (<10 min):    {quick_trips:,} ({quick_trips/len(df)*100:.1f}%)")
print(f"  Normal (10-30 min): {normal_trips:,} ({normal_trips/len(df)*100:.1f}%)")
print(f"  Long (≥30 min):     {long_duration:,} ({long_duration/len(df)*100:.1f}%)")

# 4.3 Speed analysis
print("\n4.3 Trip Speed Analysis")
print("-" * 80)

# Filter out extreme speeds for meaningful analysis
df_speed = df[(df['trip_speed_mph'] > 0) & (df['trip_speed_mph'] < 100)]
speed_stats = df_speed['trip_speed_mph'].describe()

print(f"Speed Statistics (mph):")
print(f"  Mean:      {speed_stats['mean']:.2f}")
print(f"  Median:    {df_speed['trip_speed_mph'].median():.2f}")
print(f"  Std Dev:   {speed_stats['std']:.2f}")

analysis_results["operational_analysis"]["speed"] = {
    "mean": float(speed_stats['mean']),
    "median": float(df_speed['trip_speed_mph'].median()),
    "std": float(speed_stats['std'])
}

# Speed categories
congested = (df_speed['trip_speed_mph'] < 10).sum()
moderate = ((df_speed['trip_speed_mph'] >= 10) & (df_speed['trip_speed_mph'] < 25)).sum()
fast = (df_speed['trip_speed_mph'] >= 25).sum()

print(f"\nTraffic Conditions (based on speed):")
print(f"  Heavy congestion (<10 mph):  {congested:,} ({congested/len(df_speed)*100:.1f}%)")
print(f"  Moderate (10-25 mph):        {moderate:,} ({moderate/len(df_speed)*100:.1f}%)")
print(f"  Free-flowing (≥25 mph):      {fast:,} ({fast/len(df_speed)*100:.1f}%)")

# Plot operational metrics
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# Distance distribution
axes[0, 0].hist(df[df['trip_distance'] < 20]['trip_distance'], bins=50, 
                color='steelblue', alpha=0.7, edgecolor='black')
axes[0, 0].set_xlabel('Trip Distance (miles)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Trip Distance Distribution (< 20 mi)')
axes[0, 0].axvline(distance_stats['mean'], color='red', linestyle='--', 
                   label=f'Mean: {distance_stats["mean"]:.2f} mi')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Duration distribution
axes[0, 1].hist(df[df['duration_min'] < 60]['duration_min'], bins=50, 
                color='purple', alpha=0.7, edgecolor='black')
axes[0, 1].set_xlabel('Trip Duration (minutes)')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Trip Duration Distribution (< 60 min)')
axes[0, 1].axvline(duration_stats['mean'], color='red', linestyle='--', 
                   label=f'Mean: {duration_stats["mean"]:.2f} min')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Speed distribution
axes[0, 2].hist(df_speed[df_speed['trip_speed_mph'] < 50]['trip_speed_mph'], bins=50, 
                color='orange', alpha=0.7, edgecolor='black')
axes[0, 2].set_xlabel('Trip Speed (mph)')
axes[0, 2].set_ylabel('Frequency')
axes[0, 2].set_title('Trip Speed Distribution (< 50 mph)')
axes[0, 2].axvline(speed_stats['mean'], color='red', linestyle='--', 
                   label=f'Mean: {speed_stats["mean"]:.2f} mph')
axes[0, 2].legend()
axes[0, 2].grid(alpha=0.3)

# Distance categories
dist_cat = ['Short\n(<2 mi)', 'Medium\n(2-10 mi)', 'Long\n(≥10 mi)']
axes[1, 0].bar(dist_cat, [short_trips, medium_trips, long_trips], 
               color=['lightblue', 'steelblue', 'darkblue'], alpha=0.7)
axes[1, 0].set_ylabel('Number of Trips')
axes[1, 0].set_title('Trips by Distance Category')
axes[1, 0].grid(axis='y', alpha=0.3)

# Duration categories
dur_cat = ['Quick\n(<10 min)', 'Normal\n(10-30 min)', 'Long\n(≥30 min)']
axes[1, 1].bar(dur_cat, [quick_trips, normal_trips, long_duration], 
               color=['lightgreen', 'mediumseagreen', 'darkgreen'], alpha=0.7)
axes[1, 1].set_ylabel('Number of Trips')
axes[1, 1].set_title('Trips by Duration Category')
axes[1, 1].grid(axis='y', alpha=0.3)

# Speed categories (traffic)
traffic_cat = ['Heavy\nCongestion', 'Moderate\nTraffic', 'Free-Flowing']
axes[1, 2].bar(traffic_cat, [congested, moderate, fast], 
               color=['red', 'yellow', 'green'], alpha=0.7)
axes[1, 2].set_ylabel('Number of Trips')
axes[1, 2].set_title('Traffic Conditions')
axes[1, 2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/09_operational_metrics.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 09_operational_metrics.png")

# 4.4 Passenger count analysis
print("\n4.4 Passenger Count Analysis")
print("-" * 80)

passenger_counts = df['passenger_count'].value_counts().sort_index()
print("Passenger Distribution:")
for passengers, count in passenger_counts.head(7).items():
    pct = count / len(df) * 100
    print(f"  {int(passengers)} passenger(s): {count:>8,} trips ({pct:>5.1f}%)")

analysis_results["operational_analysis"]["passenger_distribution"] = passenger_counts.head(7).to_dict()

print("\n✓ Operational analysis complete\n")

# Save complete analysis results
with open(f"{ANALYSIS_DIR}/analysis_results_complete.json", 'w') as f:
    json.dump(analysis_results, f, indent=4, default=str)

print(f"Complete analysis saved to: {ANALYSIS_DIR}/analysis_results_complete.json")
print(f"\nAnalysis complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
