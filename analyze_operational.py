"""
Operational Analysis - Chunk-based processing to avoid memory issues
Analyzes trip speed, distance, duration, and passenger patterns
"""
import pandas as pd
import numpy as np
import json
import gc

print("=" * 70)
print("OPERATIONAL ANALYSIS (Chunked Processing)")
print("=" * 70)

# Initialize aggregators
distance_sum = 0
duration_sum = 0
speed_sum = 0
passenger_sum = 0
record_count = 0

distance_values = []
duration_values = []
speed_values = []
passenger_counts = {}

chunk_size = 100000
total_processed = 0

print("\nProcessing data in chunks...\n")

# Process in chunks
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('new-clean-dataset/clean_tripdata.parquet')

for i, batch in enumerate(parquet_file.iter_batches(batch_size=chunk_size)):
    chunk = batch.to_pandas()
    
    # Aggregate sums
    distance_sum += chunk['trip_distance'].sum()
    duration_sum += chunk['duration_min'].sum()
    speed_sum += chunk['trip_speed_mph'].sum()
    passenger_sum += chunk['passenger_count'].sum()
    record_count += len(chunk)
    
    # Collect samples for percentile calculations (sample to avoid memory issues)
    if len(distance_values) < 1000000:  # Collect up to 1M samples
        distance_values.extend(chunk['trip_distance'].sample(min(1000, len(chunk))).tolist())
        duration_values.extend(chunk['duration_min'].sample(min(1000, len(chunk))).tolist())
        speed_values.extend(chunk['trip_speed_mph'].sample(min(1000, len(chunk))).tolist())
    
    # Passenger count distribution
    for passenger_count, count in chunk['passenger_count'].value_counts().items():
        passenger_counts[int(passenger_count)] = passenger_counts.get(int(passenger_count), 0) + count
    
    total_processed += len(chunk)
    
    # Clear memory
    del chunk
    gc.collect()
    
    if (i + 1) % 10 == 0:
        print(f"Processed {total_processed:,} records...")

print(f"\n✓ Total records analyzed: {total_processed:,}\n")

# Calculate statistics
avg_distance = distance_sum / record_count if record_count > 0 else 0
avg_duration = duration_sum / record_count if record_count > 0 else 0
avg_speed = speed_sum / record_count if record_count > 0 else 0
avg_passengers = passenger_sum / record_count if record_count > 0 else 0

# Percentiles from samples
distance_percentiles = {
    "25th": float(np.percentile(distance_values, 25)),
    "50th": float(np.percentile(distance_values, 50)),
    "75th": float(np.percentile(distance_values, 75)),
    "95th": float(np.percentile(distance_values, 95))
}

duration_percentiles = {
    "25th": float(np.percentile(duration_values, 25)),
    "50th": float(np.percentile(duration_values, 50)),
    "75th": float(np.percentile(duration_values, 75)),
    "95th": float(np.percentile(duration_values, 95))
}

speed_percentiles = {
    "25th": float(np.percentile(speed_values, 25)),
    "50th": float(np.percentile(speed_values, 50)),
    "75th": float(np.percentile(speed_values, 75)),
    "95th": float(np.percentile(speed_values, 95))
}

# Passenger distribution
passenger_distribution = {}
for passenger_count, count in sorted(passenger_counts.items()):
    percentage = (count / record_count * 100) if record_count > 0 else 0
    passenger_distribution[f"{passenger_count} passenger{'s' if passenger_count != 1 else ''}"] = {
        "count": int(count),
        "percentage": round(percentage, 2)
    }

# Compile results
results = {
    "total_records": record_count,
    "distance_metrics": {
        "total_miles": round(distance_sum, 2),
        "average_distance": round(avg_distance, 2),
        "percentiles": distance_percentiles
    },
    "duration_metrics": {
        "total_minutes": round(duration_sum, 2),
        "total_hours": round(duration_sum / 60, 2),
        "average_duration_minutes": round(avg_duration, 2),
        "percentiles": duration_percentiles
    },
    "speed_metrics": {
        "average_speed_mph": round(avg_speed, 2),
        "percentiles": speed_percentiles
    },
    "passenger_metrics": {
        "average_passengers": round(avg_passengers, 2),
        "distribution": passenger_distribution,
        "most_common": max(passenger_counts, key=passenger_counts.get),
        "most_common_count": passenger_counts[max(passenger_counts, key=passenger_counts.get)]
    }
}

# Save results
with open('analysis_results/operational_analysis.json', 'w') as f:
    json.dump(results, f, indent=4)

# Print key insights
print("=" * 70)
print("KEY OPERATIONAL INSIGHTS")
print("=" * 70)
print(f"\n🚗 Distance Metrics:")
print(f"   Total Miles:        {distance_sum:>12,.2f}")
print(f"   Average Distance:   {avg_distance:>12,.2f} miles")
print(f"   Median Distance:    {distance_percentiles['50th']:>12,.2f} miles")

print(f"\n⏱️  Duration Metrics:")
print(f"   Total Hours:        {duration_sum/60:>12,.2f}")
print(f"   Average Duration:   {avg_duration:>12,.2f} minutes")
print(f"   Median Duration:    {duration_percentiles['50th']:>12,.2f} minutes")

print(f"\n🏎️  Speed Metrics:")
print(f"   Average Speed:      {avg_speed:>12,.2f} mph")
print(f"   Median Speed:       {speed_percentiles['50th']:>12,.2f} mph")
print(f"   75th Percentile:    {speed_percentiles['75th']:>12,.2f} mph")

print(f"\n👥 Passenger Metrics:")
print(f"   Average Passengers: {avg_passengers:>12,.2f}")
print(f"   Most Common:        {results['passenger_metrics']['most_common']} passengers ({results['passenger_metrics']['most_common_count']:,} trips)")

print(f"\n📊 Passenger Distribution:")
for passengers, data in sorted(passenger_distribution.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
    print(f"   {passengers:15} {data['count']:>10,} ({data['percentage']:>5.1f}%)")

print("\n✓ Results saved to: analysis_results/operational_analysis.json")
print("=" * 70)
