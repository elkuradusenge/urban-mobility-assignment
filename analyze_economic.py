"""
Economic Analysis - Chunk-based processing to avoid memory issues
Analyzes fare, tips, and revenue patterns in NYC taxi data
"""
import pandas as pd
import numpy as np
import json
import gc

print("=" * 70)
print("ECONOMIC ANALYSIS (Chunked Processing)")
print("=" * 70)

# Initialize aggregators
fare_sum = 0
tip_sum = 0
toll_sum = 0
total_amount_sum = 0
record_count = 0

fare_values = []
tip_percentage_values = []
payment_type_counts = {}
tip_by_payment = {}

chunk_size = 100000
total_processed = 0

print("\nProcessing data in chunks...\n")

# Process in chunks
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('new-clean-dataset/clean_tripdata.parquet')

for i, batch in enumerate(parquet_file.iter_batches(batch_size=chunk_size)):
    chunk = batch.to_pandas()
    
    # Aggregate sums
    fare_sum += chunk['fare_amount'].sum()
    tip_sum += chunk['tip_amount'].sum()
    toll_sum += chunk['tolls_amount'].sum()
    total_amount_sum += chunk['total_amount'].sum()
    record_count += len(chunk)
    
    # Collect samples for percentile calculations (sample to avoid memory issues)
    if len(fare_values) < 1000000:  # Collect up to 1M samples
        fare_values.extend(chunk['fare_amount'].sample(min(1000, len(chunk))).tolist())
        tip_percentage_values.extend(chunk['tip_percentage'].sample(min(1000, len(chunk))).tolist())
    
    # Payment type counts
    for payment_type, count in chunk['payment_type'].value_counts().items():
        payment_type_counts[payment_type] = payment_type_counts.get(payment_type, 0) + count
    
    # Tip by payment type
    tip_by_payment_chunk = chunk.groupby('payment_type')['tip_amount'].agg(['sum', 'count']).to_dict('index')
    for payment_type, stats in tip_by_payment_chunk.items():
        if payment_type not in tip_by_payment:
            tip_by_payment[payment_type] = {'sum': 0, 'count': 0}
        tip_by_payment[payment_type]['sum'] += stats['sum']
        tip_by_payment[payment_type]['count'] += stats['count']
    
    total_processed += len(chunk)
    
    # Clear memory
    del chunk
    gc.collect()
    
    if (i + 1) % 10 == 0:
        print(f"Processed {total_processed:,} records...")

print(f"\n✓ Total records analyzed: {total_processed:,}\n")

# Calculate statistics
avg_fare = fare_sum / record_count if record_count > 0 else 0
avg_tip = tip_sum / record_count if record_count > 0 else 0
avg_toll = toll_sum / record_count if record_count > 0 else 0
avg_total = total_amount_sum / record_count if record_count > 0 else 0
avg_tip_percentage = (tip_sum / fare_sum * 100) if fare_sum > 0 else 0

# Percentiles from samples
fare_percentiles = {
    "25th": float(np.percentile(fare_values, 25)),
    "50th": float(np.percentile(fare_values, 50)),
    "75th": float(np.percentile(fare_values, 75)),
    "95th": float(np.percentile(fare_values, 95))
}

tip_percentage_percentiles = {
    "25th": float(np.percentile(tip_percentage_values, 25)),
    "50th": float(np.percentile(tip_percentage_values, 50)),
    "75th": float(np.percentile(tip_percentage_values, 75)),
    "95th": float(np.percentile(tip_percentage_values, 95))
}

# Payment type distribution
payment_type_names = {
    1: "Credit Card",
    2: "Cash",
    3: "No Charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided Trip"
}

payment_distribution = {}
for pt, count in payment_type_counts.items():
    name = payment_type_names.get(pt, f"Type {pt}")
    percentage = (count / record_count * 100) if record_count > 0 else 0
    payment_distribution[name] = {
        "count": int(count),
        "percentage": round(percentage, 2)
    }

# Average tip by payment type
avg_tip_by_payment = {}
for payment_type, stats in tip_by_payment.items():
    name = payment_type_names.get(payment_type, f"Type {payment_type}")
    avg_tip_by_payment[name] = round(stats['sum'] / stats['count'], 2) if stats['count'] > 0 else 0

# Compile results
results = {
    "total_records": record_count,
    "revenue_summary": {
        "total_fare_revenue": round(fare_sum, 2),
        "total_tip_revenue": round(tip_sum, 2),
        "total_toll_revenue": round(toll_sum, 2),
        "total_revenue": round(total_amount_sum, 2)
    },
    "average_values": {
        "average_fare": round(avg_fare, 2),
        "average_tip": round(avg_tip, 2),
        "average_toll": round(avg_toll, 2),
        "average_total": round(avg_total, 2),
        "average_tip_percentage": round(avg_tip_percentage, 2)
    },
    "fare_distribution": fare_percentiles,
    "tip_percentage_distribution": tip_percentage_percentiles,
    "payment_type_distribution": payment_distribution,
    "average_tip_by_payment_type": avg_tip_by_payment
}

# Save results
with open('analysis_results/economic_analysis.json', 'w') as f:
    json.dump(results, f, indent=4)

# Print key insights
print("=" * 70)
print("KEY ECONOMIC INSIGHTS")
print("=" * 70)
print(f"\n💰 Revenue Summary:")
print(f"   Total Revenue:      ${total_amount_sum:>15,.2f}")
print(f"   Fare Revenue:       ${fare_sum:>15,.2f}")
print(f"   Tip Revenue:        ${tip_sum:>15,.2f}")
print(f"   Toll Revenue:       ${toll_sum:>15,.2f}")

print(f"\n💵 Average Values:")
print(f"   Average Fare:       ${avg_fare:>8,.2f}")
print(f"   Average Tip:        ${avg_tip:>8,.2f}")
print(f"   Average Total:      ${avg_total:>8,.2f}")
print(f"   Average Tip %:      {avg_tip_percentage:>7.2f}%")

print(f"\n💳 Payment Distribution:")
for name, data in sorted(payment_distribution.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
    print(f"   {name:20} {data['count']:>10,} ({data['percentage']:>5.1f}%)")

print(f"\n💡 Tip Insights:")
print(f"   Median Tip %:       {tip_percentage_percentiles['50th']:>6.2f}%")
print(f"   75th Percentile:    {tip_percentage_percentiles['75th']:>6.2f}%")
print(f"   95th Percentile:    {tip_percentage_percentiles['95th']:>6.2f}%")

print("\n✓ Results saved to: analysis_results/economic_analysis.json")
print("=" * 70)
