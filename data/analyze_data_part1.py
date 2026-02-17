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

# Create analysis output directory
ANALYSIS_DIR = "analysis_results"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)

print("=" * 80)
print("NYC TAXI DATA ANALYSIS - JANUARY 2019")
print("=" * 80)
print(f"Analysis Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load data (sample for faster analysis, or full data if needed)
print("Loading data...")
DATA_FILE = "new-clean-dataset/clean_tripdata.parquet"

# Load in chunks for memory efficiency
chunk_size = 500000
df_iter = pd.read_parquet(DATA_FILE, engine='pyarrow')

# Convert datetime columns
df_iter['tpep_pickup_datetime'] = pd.to_datetime(df_iter['tpep_pickup_datetime'])
df_iter['tpep_dropoff_datetime'] = pd.to_datetime(df_iter['tpep_dropoff_datetime'])

# Extract additional temporal features for analysis
df_iter['pickup_day'] = df_iter['tpep_pickup_datetime'].dt.day
df_iter['pickup_dayofweek'] = df_iter['tpep_pickup_datetime'].dt.dayofweek
df_iter['pickup_weekday_name'] = df_iter['tpep_pickup_datetime'].dt.day_name()
df_iter['is_weekend'] = df_iter['pickup_dayofweek'].isin([5, 6]).astype(int)

print(f"Loaded {len(df_iter):,} records")
print(f"Memory usage: {df_iter.memory_usage(deep=True).sum() / 1024**3:.2f} GB\n")

# Initialize results dictionary
analysis_results = {
    "metadata": {
        "analysis_date": datetime.now().isoformat(),
        "total_records": len(df_iter),
        "data_period": "January 2019"
    },
    "temporal_analysis": {},
    "spatial_analysis": {},
    "economic_analysis": {},
    "operational_analysis": {},
    "anomalies": {}
}

print("=" * 80)
print("1. TEMPORAL ANALYSIS")
print("=" * 80)

# 1.1 Hourly patterns
print("\n1.1 Hourly Trip Distribution")
print("-" * 80)
hourly_trips = df_iter.groupby('pickup_hour').size()
hourly_avg_fare = df_iter.groupby('pickup_hour')['fare_amount'].mean()
hourly_avg_distance = df_iter.groupby('pickup_hour')['trip_distance'].mean()

peak_hour = hourly_trips.idxmax()
peak_trips = hourly_trips.max()
low_hour = hourly_trips.idxmin()
low_trips = hourly_trips.min()

print(f"Peak Hour:        {peak_hour}:00 ({peak_trips:,} trips)")
print(f"Lowest Hour:      {low_hour}:00 ({low_trips:,} trips)")
print(f"Avg trips/hour:   {hourly_trips.mean():,.0f}")
print(f"Peak vs Low:      {peak_trips/low_trips:.1f}x difference")

analysis_results["temporal_analysis"]["hourly"] = {
    "peak_hour": int(peak_hour),
    "peak_trips": int(peak_trips),
    "lowest_hour": int(low_hour),
    "lowest_trips": int(low_trips),
    "average_trips_per_hour": float(hourly_trips.mean())
}

# Plot hourly patterns
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].bar(hourly_trips.index, hourly_trips.values, color='steelblue', alpha=0.8)
axes[0].set_xlabel('Hour  of Day')
axes[0].set_ylabel('Number of Trips')
axes[0].set_title('Trip Volume by Hour')
axes[0].axvline(peak_hour, color='red', linestyle='--', label=f'Peak: {peak_hour}:00')
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

axes[1].plot(hourly_avg_fare.index, hourly_avg_fare.values, marker='o', 
             color='green', linewidth=2, markersize=6)
axes[1].set_xlabel('Hour of Day')
axes[1].set_ylabel('Average Fare ($)')
axes[1].set_title('Average Fare by Hour')
axes[1].grid(alpha=0.3)

axes[2].plot(hourly_avg_distance.index, hourly_avg_distance.values, marker='s', 
             color='orange', linewidth=2, markersize=6)
axes[2].set_xlabel('Hour of Day')
axes[2].set_ylabel('Average Distance (miles)')
axes[2].set_title('Average Trip Distance by Hour')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/01_hourly_patterns.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 01_hourly_patterns.png")

# 1.2 Day of week patterns
print("\n1.2 Day of Week Analysis")
print("-" * 80)
daily_trips = df_iter.groupby('pickup_weekday_name').size()
daily_revenue = df_iter.groupby('pickup_weekday_name')['total_amount'].sum()

# Sort by day order
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_trips = daily_trips.reindex(day_order)
daily_revenue = daily_revenue.reindex(day_order)

busiest_day = daily_trips.idxmax()
slowest_day = daily_trips.idxmin()

print(f"Busiest Day:      {busiest_day} ({daily_trips.max():,} trips)")
print(f"Slowest Day:      {slowest_day} ({daily_trips.min():,} trips)")
print(f"Weekend vs Weekday: {df_iter[df_iter['is_weekend']==1].shape[0]/df_iter[df_iter['is_weekend']==0].shape[0]:.2%} of weekday volume")

analysis_results["temporal_analysis"]["daily"] = {
    "busiest_day": busiest_day,
    "busiest_trips": int(daily_trips.max()),
    "slowest_day": slowest_day,
    "slowest_trips": int(daily_trips.min())
}

# Plot daily patterns
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

axes[0].bar(daily_trips.index, daily_trips.values, color='teal', alpha=0.8)
axes[0].set_xlabel('Day of Week')
axes[0].set_ylabel('Number of Trips')
axes[0].set_title('Trip Volume by Day of Week')
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(axis='y', alpha=0.3)

axes[1].bar(daily_revenue.index, daily_revenue.values/1e6, color='darkgreen', alpha=0.8)
axes[1].set_xlabel('Day of Week')
axes[1].set_ylabel('Total Revenue ($ Million)')
axes[1].set_title('Total Revenue by Day of Week')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/02_daily_patterns.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 02_daily_patterns.png")

# 1.3 Pickup period analysis
print("\n1.3 Pickup Period Analysis")
print("-" * 80)
period_stats = df_iter.groupby('pickup_period').agg({
    'VendorID': 'count',
    'fare_amount': 'mean',
    'tip_amount': 'mean',
    'trip_distance': 'mean',
    'trip_speed_mph': 'mean'
}).round(2)
period_stats.columns = ['Trips', 'Avg_Fare', 'Avg_Tip', 'Avg_Distance', 'Avg_Speed']

# Sort by time order
period_order = ['Morning', 'Afternoon', 'Evening', 'Night']
period_stats = period_stats.reindex(period_order)

print(period_stats)
analysis_results["temporal_analysis"]["periods"] = period_stats.to_dict()

# Plot period comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].bar(period_stats.index, period_stats['Trips'], color='purple', alpha=0.7)
axes[0, 0].set_title('Trips by Period')
axes[0, 0].set_ylabel('Number of Trips')
axes[0, 0].grid(axis='y', alpha=0.3)

axes[0, 1].bar(period_stats.index, period_stats['Avg_Fare'], color='green', alpha=0.7)
axes[0, 1].set_title('Average Fare by Period')
axes[0, 1].set_ylabel('Fare ($)')
axes[0, 1].grid(axis='y', alpha=0.3)

axes[1, 0].bar(period_stats.index, period_stats['Avg_Distance'], color='orange', alpha=0.7)
axes[1, 0].set_title('Average Distance by Period')
axes[1, 0].set_ylabel('Distance (miles)')
axes[1, 0].grid(axis='y', alpha=0.3)

axes[1, 1].bar(period_stats.index, period_stats['Avg_Speed'], color='red', alpha=0.7)
axes[1, 1].set_title('Average Speed by Period')
axes[1, 1].set_ylabel('Speed (mph)')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/03_period_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   ✓ Saved: 03_period_analysis.png")

print("\n✓ Temporal analysis complete\n")

# Continue with spatial analysis
print("=" * 80)
print("2. SPATIAL ANALYSIS")
print("=" * 80)

# 2.1 Borough analysis
print("\n2.1 Borough Distribution")
print("-" * 80)

# Pickup borough analysis
pu_borough_trips = df_iter['PU_Borough'].value_counts()
pu_borough_revenue = df_iter.groupby('PU_Borough')['total_amount'].sum()

print("Top Pickup Boroughs:")
for borough, count in pu_borough_trips.head().items():
    pct = count / len(df_iter) * 100
    revenue = pu_borough_revenue[borough]
    print(f"  {borough:<20} {count:>10,} trips ({pct:>5.1f}%)  ${revenue:>12,.0f} revenue")

analysis_results["spatial_analysis"]["top_pickup_boroughs"] = pu_borough_trips.head(5).to_dict()

# Dropoff borough analysis
do_borough_trips = df_iter['DO_Borough'].value_counts()
print("\nTop Dropoff Boroughs:")
for borough, count in do_borough_trips.head().items():
    pct = count / len(df_iter) * 100
    print(f"  {borough:<20} {count:>10,} trips ({pct:>5.1f}%)")

# Plot borough analysis
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Filter out Unknown
pu_borough_trips_clean = pu_borough_trips[pu_borough_trips.index != 'Unknown']
axes[0].pie(pu_borough_trips_clean.values, labels=pu_borough_trips_clean.index, 
            autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2"))
axes[0].set_title('Pickup Borough Distribution')

do_borough_trips_clean = do_borough_trips[do_borough_trips.index != 'Unknown']
axes[1].pie(do_borough_trips_clean.values, labels=do_borough_trips_clean.index, 
            autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3"))
axes[1].set_title('Dropoff Borough Distribution')

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/04_borough_distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"\n   ✓ Saved: 04_borough_distribution.png")

# 2.2 Popular zones
print("\n2.2 Popular Zones")
print("-" * 80)

top_pickup_zones = df_iter['PU_Zone'].value_counts().head(10)
top_dropoff_zones = df_iter['DO_Zone'].value_counts().head(10)

print("Top 10 Pickup Zones:")
for i, (zone, count) in enumerate(top_pickup_zones.items(), 1):
    print(f"  {i:>2}. {zone:<40} {count:>8,} trips")

analysis_results["spatial_analysis"]["top_pickup_zones"] = top_pickup_zones.head(10).to_dict()

print("\nTop 10 Dropoff Zones:")
for i, (zone, count) in enumerate(top_dropoff_zones.items(), 1):
    print(f"  {i:>2}. {zone:<40} {count:>8,} trips")

# Plot top zones
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

axes[0].barh(range(len(top_pickup_zones)), top_pickup_zones.values, color='steelblue', alpha=0.8)
axes[0].set_yticks(range(len(top_pickup_zones)))
axes[0].set_yticklabels(top_pickup_zones.index, fontsize=9)
axes[0].set_xlabel('Number of Trips')
axes[0].set_title('Top 10 Pickup Zones')
axes[0].grid(axis='x', alpha=0.3)
axes[0].invert_yaxis()

axes[1].barh(range(len(top_dropoff_zones)), top_dropoff_zones.values, color='coral', alpha=0.8)
axes[1].set_yticks(range(len(top_dropoff_zones)))
axes[1].set_yticklabels(top_dropoff_zones.index, fontsize=9)
axes[1].set_xlabel('Number of Trips')
axes[1].set_title('Top 10 Dropoff Zones')
axes[1].grid(axis='x', alpha=0.3)
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig(f"{ANALYSIS_DIR}/05_top_zones.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"\n   ✓ Saved: 05_top_zones.png")

# 2.3 Popular routes
print("\n2.3 Popular Routes")
print("-" * 80)

df_iter['route'] = df_iter['PU_Zone'] + ' → ' + df_iter['DO_Zone']
top_routes = df_iter['route'].value_counts().head(15)

print("Top 15 Routes:")
for i, (route, count) in enumerate(top_routes.items(), 1):
    print(f"  {i:>2}. {route:<60} {count:>6,} trips")

analysis_results["spatial_analysis"]["top_routes"] = top_routes.head(15).to_dict()

print("\n✓ Spatial analysis complete\n")

# Save analysis results so far
with open(f"{ANALYSIS_DIR}/analysis_results_part1.json", 'w') as f:
    json.dump(analysis_results, f, indent=4, default=str)

print(f"Analysis progress saved to: {ANALYSIS_DIR}/analysis_results_part1.json")
print(f"\nContinuing to Part 2...\n")
