"""
Spatial Analysis - Chunk-based processing to avoid memory issues
Analyzes location-based patterns in NYC taxi data
"""
import pandas as pd
import json
import gc
from collections import defaultdict

print("=" * 70)
print("SPATIAL ANALYSIS (Chunked Processing)")
print("=" * 70)

# Initialize aggregators
pickup_zone_counts = defaultdict(int)
dropoff_zone_counts = defaultdict(int)
pickup_borough_counts = defaultdict(int)
dropoff_borough_counts = defaultdict(int)
route_counts = defaultdict(int)
zone_revenue = defaultdict(float)

chunk_size = 100000
total_processed = 0

print("\nProcessing data in chunks...\n")

# Process in chunks
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('new-clean-dataset/clean_tripdata.parquet')

for i, batch in enumerate(parquet_file.iter_batches(batch_size=chunk_size)):
    chunk = batch.to_pandas()
    
    # Pickup zone counts
    for zone, count in chunk['PU_Zone'].value_counts().items():
        if pd.notna(zone):
            pickup_zone_counts[zone] += count
    
    # Dropoff zone counts
    for zone, count in chunk['DO_Zone'].value_counts().items():
        if pd.notna(zone):
            dropoff_zone_counts[zone] += count
    
    # Pickup borough counts
    for borough, count in chunk['PU_Borough'].value_counts().items():
        if pd.notna(borough):
            pickup_borough_counts[borough] += count
    
    # Dropoff borough counts
    for borough, count in chunk['DO_Borough'].value_counts().items():
        if pd.notna(borough):
            dropoff_borough_counts[borough] += count
    
    # Popular routes (top combinations only to save memory)
    chunk['route'] = chunk['PU_Zone'].astype(str) + ' → ' + chunk['DO_Zone'].astype(str)
    for route, count in chunk['route'].value_counts().head(1000).items():
        route_counts[route] += count
    
    # Zone revenue (pickup zones)
    zone_rev = chunk.groupby('PU_Zone')['total_amount'].sum()
    for zone, revenue in zone_rev.items():
        if pd.notna(zone):
            zone_revenue[zone] += revenue
    
    total_processed += len(chunk)
    
    # Clear memory
    del chunk
    gc.collect()
    
    if (i + 1) % 10 == 0:
        print(f"Processed {total_processed:,} records...")

print(f"\n✓ Total records analyzed: {total_processed:,}\n")

# Get top 20 for each category
top_pickup_zones = dict(sorted(pickup_zone_counts.items(), key=lambda x: x[1], reverse=True)[:20])
top_dropoff_zones = dict(sorted(dropoff_zone_counts.items(), key=lambda x: x[1], reverse=True)[:20])
top_routes = dict(sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:20])
top_revenue_zones = dict(sorted(zone_revenue.items(), key=lambda x: x[1], reverse=True)[:20])

# Compile results
results = {
    "pickup_zones": {
        "top_20": top_pickup_zones,
        "total_zones": len(pickup_zone_counts),
        "most_popular": max(pickup_zone_counts, key=pickup_zone_counts.get),
        "most_popular_count": pickup_zone_counts[max(pickup_zone_counts, key=pickup_zone_counts.get)]
    },
    "dropoff_zones": {
        "top_20": top_dropoff_zones,
        "total_zones": len(dropoff_zone_counts),
        "most_popular": max(dropoff_zone_counts, key=dropoff_zone_counts.get),
        "most_popular_count": dropoff_zone_counts[max(dropoff_zone_counts, key=dropoff_zone_counts.get)]
    },
    "pickup_boroughs": {
        "distribution": dict(pickup_borough_counts),
        "most_popular": max(pickup_borough_counts, key=pickup_borough_counts.get) if pickup_borough_counts else None,
        "most_popular_count": pickup_borough_counts[max(pickup_borough_counts, key=pickup_borough_counts.get)] if pickup_borough_counts else 0
    },
    "dropoff_boroughs": {
        "distribution": dict(dropoff_borough_counts),
        "most_popular": max(dropoff_borough_counts, key=dropoff_borough_counts.get) if dropoff_borough_counts else None,
        "most_popular_count": dropoff_borough_counts[max(dropoff_borough_counts, key=dropoff_borough_counts.get)] if dropoff_borough_counts else 0
    },
    "popular_routes": {
        "top_20": top_routes,
        "most_popular_route": max(route_counts, key=route_counts.get),
        "most_popular_count": route_counts[max(route_counts, key=route_counts.get)]
    },
    "zone_revenue": {
        "top_20": {k: round(v, 2) for k, v in top_revenue_zones.items()},
        "highest_revenue_zone": max(zone_revenue, key=zone_revenue.get),
        "highest_revenue_amount": round(zone_revenue[max(zone_revenue, key=zone_revenue.get)], 2)
    }
}

# Save results
with open('analysis_results/spatial_analysis.json', 'w') as f:
    json.dump(results, f, indent=4)

# Print key insights
print("=" * 70)
print("KEY SPATIAL INSIGHTS")
print("=" * 70)
print(f"\n📍 Pickup Zones:")
print(f"   Most Popular:     {results['pickup_zones']['most_popular']}")
print(f"   Pickups:          {results['pickup_zones']['most_popular_count']:,}")
print(f"   Total Zones:      {results['pickup_zones']['total_zones']}")

print(f"\n📍 Dropoff Zones:")
print(f"   Most Popular:     {results['dropoff_zones']['most_popular']}")
print(f"   Dropoffs:         {results['dropoff_zones']['most_popular_count']:,}")

print(f"\n🏙️  Borough Distribution (Pickups):")
for borough, count in sorted(pickup_borough_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_processed * 100) if total_processed > 0 else 0
    print(f"   {borough:20} {count:>10,} ({percentage:>5.1f}%)")

print(f"\n🚕 Popular Routes:")
print(f"   Most Popular:     {results['popular_routes']['most_popular_route']}")
print(f"   Trips:            {results['popular_routes']['most_popular_count']:,}")

print(f"\n💰 Highest Revenue Zone:")
print(f"   Zone:             {results['zone_revenue']['highest_revenue_zone']}")
print(f"   Revenue:          ${results['zone_revenue']['highest_revenue_amount']:,.2f}")

print("\n✓ Results saved to: analysis_results/spatial_analysis.json")
print("=" * 70)
