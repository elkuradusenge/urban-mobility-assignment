"""
Temporal Analysis - Chunk-based processing to avoid memory issues
Analyzes time-based patterns in NYC taxi data
"""
import pandas as pd
import json
import gc
from collections import defaultdict

print("=" * 70)
print("TEMPORAL ANALYSIS (Chunked Processing)")
print("=" * 70)

# Initialize aggregators
hourly_counts = defaultdict(int)
daily_counts = defaultdict(int)
period_counts = defaultdict(int)
hourly_revenue = defaultdict(float)
day_of_week_counts = defaultdict(int)

chunk_size = 100000
total_processed = 0

print("\nProcessing data in chunks...\n")

# Process in chunks to avoid memory issues
# Use pyarrow ParquetFile for chunked reading
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('new-clean-dataset/clean_tripdata.parquet')

for i, batch in enumerate(parquet_file.iter_batches(batch_size=chunk_size)):
    chunk = batch.to_pandas()
    
    # Convert to datetime if not already
    chunk['tpep_pickup_datetime'] = pd.to_datetime(chunk['tpep_pickup_datetime'])
    
    # Extract temporal features
    chunk['hour'] = chunk['tpep_pickup_datetime'].dt.hour
    chunk['day'] = chunk['tpep_pickup_datetime'].dt.day
    chunk['day_of_week'] = chunk['tpep_pickup_datetime'].dt.dayofweek
    chunk['day_name'] = chunk['tpep_pickup_datetime'].dt.day_name()
    
    # Aggregate hourly patterns
    for hour, count in chunk['hour'].value_counts().items():
        hourly_counts[hour] += count
    
    # Aggregate daily patterns
    for day, count in chunk['day'].value_counts().items():
        daily_counts[day] += count
    
    # Aggregate period patterns
    for period, count in chunk['pickup_period'].value_counts().items():
        period_counts[period] += count
    
    # Aggregate hourly revenue
    hourly_rev = chunk.groupby('hour')['total_amount'].sum()
    for hour, revenue in hourly_rev.items():
        hourly_revenue[hour] += revenue
    
    # Aggregate day of week patterns
    for day_name, count in chunk['day_name'].value_counts().items():
        day_of_week_counts[day_name] += count
    
    total_processed += len(chunk)
    
    # Clear memory
    del chunk
    gc.collect()
    
    if (i + 1) % 10 == 0:
        print(f"Processed {total_processed:,} records...")

print(f"\n✓ Total records analyzed: {total_processed:,}\n")

# Compile results
results = {
    "hourly_distribution": {
        "data": dict(sorted(hourly_counts.items())),
        "peak_hour": max(hourly_counts, key=hourly_counts.get),
        "peak_hour_trips": hourly_counts[max(hourly_counts, key=hourly_counts.get)],
        "off_peak_hour": min(hourly_counts, key=hourly_counts.get),
        "off_peak_trips": hourly_counts[min(hourly_counts, key=hourly_counts.get)]
    },
    "period_distribution": {
        "data": dict(period_counts),
        "busiest_period": max(period_counts, key=period_counts.get),
        "busiest_period_trips": period_counts[max(period_counts, key=period_counts.get)]
    },
    "daily_distribution": {
        "data": dict(sorted(daily_counts.items())),
        "busiest_day": max(daily_counts, key=daily_counts.get),
        "busiest_day_trips": daily_counts[max(daily_counts, key=daily_counts.get)]
    },
    "day_of_week_distribution": {
        "data": dict(day_of_week_counts),
        "busiest_weekday": max(day_of_week_counts, key=day_of_week_counts.get),
        "busiest_weekday_trips": day_of_week_counts[max(day_of_week_counts, key=day_of_week_counts.get)]
    },
    "hourly_revenue": {
        "data": {k: round(v, 2) for k, v in sorted(hourly_revenue.items())},
        "peak_revenue_hour": max(hourly_revenue, key=hourly_revenue.get),
        "peak_revenue_amount": round(hourly_revenue[max(hourly_revenue, key=hourly_revenue.get)], 2)
    }
}

# Save results
with open('analysis_results/temporal_analysis.json', 'w') as f:
    json.dump(results, f, indent=4)

# Print key insights
print("=" * 70)
print("KEY TEMPORAL INSIGHTS")
print("=" * 70)
print(f"\n📊 Hourly Patterns:")
print(f"   Peak Hour:        {results['hourly_distribution']['peak_hour']}:00 ({results['hourly_distribution']['peak_hour_trips']:,} trips)")
print(f"   Off-Peak Hour:    {results['hourly_distribution']['off_peak_hour']}:00 ({results['hourly_distribution']['off_peak_trips']:,} trips)")

print(f"\n📊 Period Patterns:")
print(f"   Busiest Period:   {results['period_distribution']['busiest_period']} ({results['period_distribution']['busiest_period_trips']:,} trips)")

print(f"\n📊 Day of Week:")
print(f"   Busiest Day:      {results['day_of_week_distribution']['busiest_weekday']} ({results['day_of_week_distribution']['busiest_weekday_trips']:,} trips)")

print(f"\n💰 Revenue Patterns:")
print(f"   Peak Revenue Hour: {results['hourly_revenue']['peak_revenue_hour']}:00 (${results['hourly_revenue']['peak_revenue_amount']:,.2f})")

print("\n✓ Results saved to: analysis_results/temporal_analysis.json")
print("=" * 70)
