import pandas as pd
import numpy as np
import os
import json
import gc
import psutil
from datetime import datetime

# Paths
ORIGINAL_DIR = "old-original"
CLEAN_DIR = "new-clean-dataset"
LOG_FILE = "data_cleaning_log.json"
CHECKPOINT_FILE = "processing_checkpoint.json"

# File names
TRIP_DATA = "yellow_tripdata_2019-01.csv"
ZONE_LOOKUP = "taxi_zone_lookup.csv"

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def save_checkpoint(chunk_number, stats):
    """Save processing checkpoint"""
    checkpoint = {
        "last_chunk": chunk_number,
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=4)

def load_checkpoint():
    """Load processing checkpoint if exists"""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return None

def process_data():
    print("=" * 70)
    print("NYC TAXI DATA PROCESSING PIPELINE (SAFE MODE)")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Initial Memory Usage: {get_memory_usage():.2f} MB\n")
    
    # Ensure directories exist
    if not os.path.exists(CLEAN_DIR):
        os.makedirs(CLEAN_DIR)

    # Load lookup data (small file, safe to load fully)
    print("Loading zone lookup data...")
    zone_lookup = pd.read_csv(os.path.join(ORIGINAL_DIR, ZONE_LOOKUP))
    print(f"Zones loaded: {len(zone_lookup)} zones\n")
    
    # Check for checkpoint
    checkpoint = load_checkpoint()
    start_chunk = 0
    
    excluded_stats = {
        "initial_total_records": 0,
        "missing_values": 0,
        "duplicates": 0,
        "outliers_distance": 0,
        "outliers_fare": 0,
        "outliers_time": 0,
        "final_clean_records": 0
    }
    
    if checkpoint:
        print(f"⚠️  CHECKPOINT FOUND: Resuming from chunk {checkpoint['last_chunk'] + 1}")
        print(f"   Previous run: {checkpoint['timestamp']}")
        start_chunk = checkpoint['last_chunk'] + 1
        excluded_stats = checkpoint['stats']
        first_chunk = False
        print(f"   Records processed so far: {excluded_stats['final_clean_records']:,}\n")
    else:
        first_chunk = True
        print("Starting fresh processing...\n")
    
    output_csv = os.path.join(CLEAN_DIR, "clean_tripdata.csv")
    output_parquet = os.path.join(CLEAN_DIR, "clean_tripdata.parquet")
    
    # Remove existing files only if starting fresh
    if start_chunk == 0:
        if os.path.exists(output_csv):
            os.remove(output_csv)
        if os.path.exists(output_parquet):
            os.remove(output_parquet)
    
    # Smaller chunk size for stability (adjust based on your RAM)
    chunk_size = 50000  # Reduced from 100K
    progress_update_frequency = 5  # Update every 5 chunks
    checkpoint_frequency = 20  # Save checkpoint every 20 chunks
    
    print(f"Configuration:")
    print(f"  - Chunk size: {chunk_size:,} rows")
    print(f"  - Progress updates: Every {progress_update_frequency} chunks")
    print(f"  - Checkpoints: Every {checkpoint_frequency} chunks")
    print("\n" + "=" * 70)
    print("PROCESSING DATA...")
    print("=" * 70 + "\n")
    
    try:
        # Stream data in chunks
        reader = pd.read_csv(
            os.path.join(ORIGINAL_DIR, TRIP_DATA), 
            chunksize=chunk_size, 
            low_memory=False,
            skiprows=range(1, start_chunk * chunk_size + 1) if start_chunk > 0 else None
        )
    except FileNotFoundError:
        print(f"❌ Error: {TRIP_DATA} not found in {ORIGINAL_DIR}")
        return
    
    chunk_counter = start_chunk
    
    try:
        for i, chunk in enumerate(reader):
            actual_chunk_num = chunk_counter + i
            initial_chunk_count = len(chunk)
            excluded_stats["initial_total_records"] += initial_chunk_count
            
            # ===== DATA CLEANING =====
            
            # A. Remove missing values in critical columns
            chunk = chunk.dropna(subset=['PULocationID', 'DOLocationID', 
                                        'tpep_pickup_datetime', 'tpep_dropoff_datetime'])
            excluded_stats["missing_values"] += (initial_chunk_count - len(chunk))
            
            # B. Remove duplicates
            count_before_dup = len(chunk)
            chunk = chunk.drop_duplicates()
            excluded_stats["duplicates"] += (count_before_dup - len(chunk))
            
            # C. Standardize timestamps
            chunk['tpep_pickup_datetime'] = pd.to_datetime(chunk['tpep_pickup_datetime'], errors='coerce')
            chunk['tpep_dropoff_datetime'] = pd.to_datetime(chunk['tpep_dropoff_datetime'], errors='coerce')
            chunk = chunk.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
            
            # D. Remove outliers
            # Distance: 0 < distance < 100 miles
            count_before_dist = len(chunk)
            chunk = chunk[(chunk['trip_distance'] > 0) & (chunk['trip_distance'] < 100)]
            excluded_stats["outliers_distance"] += (count_before_dist - len(chunk))
            
            # Fare: 0 < fare < $1000
            count_before_fare = len(chunk)
            chunk = chunk[(chunk['fare_amount'] > 0) & (chunk['fare_amount'] < 1000)]
            excluded_stats["outliers_fare"] += (count_before_fare - len(chunk))
            
            # Duration: 0 < duration < 6 hours
            count_before_time = len(chunk)
            chunk['duration_min'] = (chunk['tpep_dropoff_datetime'] - 
                                    chunk['tpep_pickup_datetime']).dt.total_seconds() / 60
            chunk = chunk[(chunk['duration_min'] > 0) & (chunk['duration_min'] < 360)]
            excluded_stats["outliers_time"] += (count_before_time - len(chunk))
            
            # ===== FEATURE ENGINEERING =====
            
            # Feature 1: Trip Speed (mph)
            chunk['trip_speed_mph'] = chunk['trip_distance'] / (chunk['duration_min'] / 60)
            chunk['trip_speed_mph'] = chunk['trip_speed_mph'].replace([np.inf, -np.inf], 0)
            
            # Feature 2: Tip Percentage
            chunk['tip_percentage'] = np.where(
                chunk['fare_amount'] > 0, 
                (chunk['tip_amount'] / chunk['fare_amount']) * 100, 
                0
            )
            
            # Feature 3: Pickup Period
            def get_period(hour):
                if 5 <= hour < 12: return 'Morning'
                elif 12 <= hour < 17: return 'Afternoon'
                elif 17 <= hour < 21: return 'Evening'
                else: return 'Night'
            
            chunk['pickup_hour'] = chunk['tpep_pickup_datetime'].dt.hour
            chunk['pickup_period'] = chunk['pickup_hour'].apply(get_period)
            
            # ===== DATA INTEGRATION =====
            
            # Merge Pickup Location Info
            chunk = chunk.merge(zone_lookup, left_on='PULocationID', right_on='LocationID', how='left')
            chunk = chunk.rename(columns={
                'Borough': 'PU_Borough', 
                'Zone': 'PU_Zone', 
                'service_zone': 'PU_ServiceZone'
            }).drop('LocationID', axis=1)
            
            # Merge Dropoff Location Info
            chunk = chunk.merge(zone_lookup, left_on='DOLocationID', right_on='LocationID', how='left')
            chunk = chunk.rename(columns={
                'Borough': 'DO_Borough', 
                'Zone': 'DO_Zone', 
                'service_zone': 'DO_ServiceZone'
            }).drop('LocationID', axis=1)
            
            # ===== INCREMENTAL SAVE =====
            
            # Write to CSV incrementally (memory-safe)
            chunk.to_csv(output_csv, mode='a', header=first_chunk, index=False)
            first_chunk = False
            
            excluded_stats["final_clean_records"] += len(chunk)
            
            # Clear chunk from memory
            del chunk
            gc.collect()
            
            # ===== PROGRESS UPDATES =====
            
            if (i + 1) % progress_update_frequency == 0:
                records_processed = (actual_chunk_num + 1) * chunk_size
                mem_usage = get_memory_usage()
                retention_rate = (excluded_stats["final_clean_records"] / 
                                excluded_stats["initial_total_records"] * 100) if excluded_stats["initial_total_records"] > 0 else 0
                
                print(f"Chunk {actual_chunk_num + 1:>4} | "
                      f"Raw: {records_processed:>9,} | "
                      f"Clean: {excluded_stats['final_clean_records']:>9,} | "
                      f"Retention: {retention_rate:>5.1f}% | "
                      f"Memory: {mem_usage:>7.1f} MB")
            
            # ===== CHECKPOINT SAVE =====
            
            if (i + 1) % checkpoint_frequency == 0:
                save_checkpoint(actual_chunk_num, excluded_stats)
                print(f"   ✓ Checkpoint saved at chunk {actual_chunk_num + 1}")
        
        # Save final checkpoint
        save_checkpoint(actual_chunk_num, excluded_stats)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  PROCESSING INTERRUPTED BY USER")
        print(f"Progress saved at chunk {actual_chunk_num}")
        print("Run script again to resume from checkpoint.")
        return
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        print(f"Progress saved at chunk {actual_chunk_num}")
        print("Run script again to resume from checkpoint.")
        raise
    
    # ===== CONVERT TO PARQUET (CHUNKED, MEMORY-SAFE) =====
    
    print("\n" + "=" * 70)
    print("CONVERTING TO PARQUET FORMAT (Chunked)...")
    print("=" * 70 + "\n")
    
    # Remove old parquet if exists
    if os.path.exists(output_parquet):
        os.remove(output_parquet)
    
    # Use PyArrow directly for better control over chunked writing
    import pyarrow as pa
    import pyarrow.parquet as pq
    
    # Convert in chunks to avoid memory overload
    parquet_chunk_size = 100000
    parquet_reader = pd.read_csv(output_csv, chunksize=parquet_chunk_size)
    
    parquet_writer = None
    for j, parquet_chunk in enumerate(parquet_reader):
        table = pa.Table.from_pandas(parquet_chunk)
        
        if parquet_writer is None:
            # Create writer on first chunk
            parquet_writer = pq.ParquetWriter(output_parquet, table.schema)
        
        parquet_writer.write_table(table)
        
        if (j + 1) % 10 == 0:
            print(f"  Converted {(j + 1) * parquet_chunk_size:,} rows to Parquet...")
        
        del parquet_chunk, table
        gc.collect()
    
    if parquet_writer:
        parquet_writer.close()
    
    print(f"  ✓ Parquet conversion complete\n")
    
    # ===== SAVE FINAL LOG =====
    
    with open(os.path.join(CLEAN_DIR, LOG_FILE), 'w') as f:
        json.dump(excluded_stats, f, indent=4)
    
    # Clean up checkpoint file
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    
    # ===== FINAL SUMMARY =====
    
    print("=" * 70)
    print("PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"\n📊 DATA SUMMARY:")
    print(f"   Total Raw Records:      {excluded_stats['initial_total_records']:>12,}")
    print(f"   Final Clean Records:    {excluded_stats['final_clean_records']:>12,}")
    print(f"   Overall Retention:      {(excluded_stats['final_clean_records']/excluded_stats['initial_total_records']*100):>11.2f}%")
    
    print(f"\n🗑️  EXCLUDED RECORDS:")
    print(f"   Missing Values:         {excluded_stats['missing_values']:>12,}")
    print(f"   Duplicates:             {excluded_stats['duplicates']:>12,}")
    print(f"   Distance Outliers:      {excluded_stats['outliers_distance']:>12,}")
    print(f"   Fare Outliers:          {excluded_stats['outliers_fare']:>12,}")
    print(f"   Time Outliers:          {excluded_stats['outliers_time']:>12,}")
    total_excluded = (excluded_stats['missing_values'] + excluded_stats['duplicates'] + 
                     excluded_stats['outliers_distance'] + excluded_stats['outliers_fare'] + 
                     excluded_stats['outliers_time'])
    print(f"   Total Excluded:         {total_excluded:>12,}")
    
    print(f"\n💾 OUTPUT FILES:")
    print(f"   CSV:     {output_csv}")
    print(f"   Parquet: {output_parquet}")
    print(f"   Log:     {os.path.join(CLEAN_DIR, LOG_FILE)}")
    
    print(f"\n🕒 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 Final Memory Usage: {get_memory_usage():.2f} MB")
    print("=" * 70)

if __name__ == "__main__":
    process_data()
