import json
import os
import pyarrow.parquet as pq

# ============================================================
# CONFIGURATION: Set to 'sample' or 'full'
# ============================================================
MODE = 'full'  # Options: 'sample' (fast, 1000 records) or 'full' (complete dataset with batches)
BATCH_SIZE = 100000  # For 'full' mode: number of records per batch
# ============================================================

print("=" * 70)
print("DATA QUALITY VERIFICATION REPORT")
print(f"Running in: {MODE.upper()} MODE")
print("=" * 70)
print()

# Load cleaning log
with open('new-clean-dataset/data_cleaning_log.json', 'r') as f:
    log = json.load(f)

stats = log['stats']

print("1. DATA CLEANING SUMMARY")
print("-" * 70)
print(f"   Initial Raw Records:        {stats['initial_total_records']:>12,}")
print(f"   Final Clean Records:        {stats['final_clean_records']:>12,}")
print(f"   Overall Retention Rate:     {(stats['final_clean_records']/stats['initial_total_records']*100):>11.2f}%")
print()
print(f"   Records Excluded:")
print(f"     - Missing Values:         {stats['missing_values']:>12,}")
print(f"     - Duplicates:             {stats['duplicates']:>12,}")
print(f"     - Distance Outliers:      {stats['outliers_distance']:>12,} (>100 miles or ≤0)")
print(f"     - Fare Outliers:          {stats['outliers_fare']:>12,} (>$1000 or ≤0)")
print(f"     - Time Outliers:          {stats['outliers_time']:>12,} (>6 hrs or ≤0)")
total_excluded = sum([stats['missing_values'], stats['duplicates'], 
                     stats['outliers_distance'], stats['outliers_fare'], stats['outliers_time']])
print(f"     - Total Excluded:         {total_excluded:>12,}")
print()

# Verify file sizes
csv_file = 'new-clean-dataset/clean_tripdata.csv'
parquet_file = 'new-clean-dataset/clean_tripdata.parquet'

print("2. OUTPUT FILE VERIFICATION")
print("-" * 70)
if os.path.exists(csv_file):
    csv_size = os.path.getsize(csv_file) / (1024**3)  # GB
    print(f"   ✓ CSV File:     {csv_file}")
    print(f"     Size:         {csv_size:.2f} GB")
else:
    print(f"   ✗ CSV File:     NOT FOUND")

if os.path.exists(parquet_file):
    parquet_size = os.path.getsize(parquet_file) / (1024**3)  # GB
    print(f"   ✓ Parquet File: {parquet_file}")
    print(f"     Size:         {parquet_size:.2f} GB")
    print(f"     Compression:  {(1 - parquet_size/csv_size)*100:.1f}% smaller than CSV")
else:
    print(f"   ✗ Parquet File: NOT FOUND")
print()


print("3. DATA SAMPLE & SCHEMA VERIFICATION")
print("-" * 70)
print("   Loading sample data from Parquet (memory-efficient mode)...")

parquet_table = pq.read_table(parquet_file, memory_map=True)
total_rows = parquet_table.num_rows
sample_size = min(1000, total_rows)

# Read only the first batch efficiently
df_sample = parquet_table.slice(0, sample_size).to_pandas()

# Clean up memory
del parquet_table

print(f"   Records sampled: {len(df_sample):,} out of {total_rows:,}")
print(f"   Total columns:   {len(df_sample.columns)}")
print()
print("   Column Overview:")
for col in df_sample.columns:
    dtype = df_sample[col].dtype
    nulls = df_sample[col].isnull().sum()
    print(f"     {col:<30} {str(dtype):<15} (nulls: {nulls})")

print()
print("4. ENGINEERED FEATURES VERIFICATION")
print("-" * 70)
if 'trip_speed_mph' in df_sample.columns:
    print(f"   ✓ trip_speed_mph:    Min={df_sample['trip_speed_mph'].min():.2f}, "
          f"Max={df_sample['trip_speed_mph'].max():.2f}, "
          f"Mean={df_sample['trip_speed_mph'].mean():.2f}")
if 'tip_percentage' in df_sample.columns:
    print(f"   ✓ tip_percentage:    Min={df_sample['tip_percentage'].min():.2f}%, "
          f"Max={df_sample['tip_percentage'].max():.2f}%, "
          f"Mean={df_sample['tip_percentage'].mean():.2f}%")
if 'pickup_period' in df_sample.columns:
    print(f"   ✓ pickup_period:     {df_sample['pickup_period'].unique()}")
if 'PU_Borough' in df_sample.columns and 'DO_Borough' in df_sample.columns:
    print(f"   ✓ Borough Integration: {df_sample['PU_Borough'].nunique()} pickup boroughs, "
          f"{df_sample['DO_Borough'].nunique()} dropoff boroughs")

print()
print("5. DATA QUALITY CHECKS")
print("-" * 70)

# Check for issues in sample
issues = []
if df_sample['trip_distance'].min() <= 0:
    issues.append("   ⚠ Negative/zero trip distances found in sample")
if df_sample['fare_amount'].min() <= 0:
    issues.append("   ⚠ Negative/zero fares found in sample")
if df_sample['duration_min'].min() <= 0:
    issues.append("   ⚠ Negative/zero durations found in sample")

if not issues:
    print("   ✓ No data quality issues detected in sample")
    print("   ✓ All trip distances > 0")
    print("   ✓ All fares > 0")
    print("   ✓ All durations > 0")
else:
    for issue in issues:
        print(issue)

# Batch verification for full dataset (controlled by MODE variable)
if MODE == 'full':
    print()
    print("6. BATCH VERIFICATION (Processing in chunks...)")
    print("-" * 70)
    parquet_file_obj = pq.ParquetFile(parquet_file)
    total_batches = (parquet_file_obj.metadata.num_rows + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"   Total records: {parquet_file_obj.metadata.num_rows:,}")
    print(f"   Batch size: {BATCH_SIZE:,}")
    print(f"   Number of batches: {total_batches}")
    
    batch_issues = 0
    for i, batch in enumerate(parquet_file_obj.iter_batches(batch_size=BATCH_SIZE)):
        df_batch = batch.to_pandas()
        
        # Check for issues in this batch
        if (df_batch['trip_distance'].min() <= 0 or 
            df_batch['fare_amount'].min() <= 0 or 
            df_batch['duration_min'].min() <= 0):
            batch_issues += 1
        
        # Clean up batch from memory
        del df_batch
        
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{total_batches} batches...")
    
    if batch_issues == 0:
        print(f"   ✓ All {total_batches} batches passed quality checks")
    else:
        print(f"   ⚠ {batch_issues} batches contained data quality issues")

print()
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
if MODE == 'sample':
    print()
    print("NOTE: Running in SAMPLE mode (1000 records).")
    print("      To verify the full dataset, set MODE = 'full' at the top of the script.")
elif MODE == 'full':
    print()
    print("NOTE: Full dataset verification completed using batch processing.")
