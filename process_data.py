import pandas as pd
import numpy as np
import os
import json

# Paths
ORIGINAL_DIR = "old-original"
CLEAN_DIR = "new-clean-dataset"
LOG_FILE = "data_cleaning_log.json"

# File names
TRIP_DATA = "yellow_tripdata_2019-01.csv"
ZONE_LOOKUP = "taxi_zone_lookup.csv"

def process_data():
    print("Initializing Data Processing Pipeline...")
    
    # Ensure directories exist
    if not os.path.exists(CLEAN_DIR):
        os.makedirs(CLEAN_DIR)

    # 1. Pipeline to load data
    print("Loading Trip Data (Streaming Chunks - Memory Optimized)...")
    chunk_size = 100000  # Reduced chunk size for better memory management
    try:
        reader = pd.read_csv(os.path.join(ORIGINAL_DIR, TRIP_DATA), chunksize=chunk_size, low_memory=False)
    except FileNotFoundError:
        print(f"Error: {TRIP_DATA} not found in {ORIGINAL_DIR}")
        return

    # Load lookup data
    zone_lookup = pd.read_csv(os.path.join(ORIGINAL_DIR, ZONE_LOOKUP))
    
    excluded_stats = {
        "initial_total_records": 0,
        "missing_values": 0,
        "duplicates": 0,
        "outliers_distance": 0,
        "outliers_fare": 0,
        "outliers_time": 0,
        "final_clean_records": 0
    }
    
    # Write header first
    first_chunk = True
    output_csv = os.path.join(CLEAN_DIR, "clean_tripdata.csv")
    output_parquet = os.path.join(CLEAN_DIR, "clean_tripdata.parquet")
    
    print("Cleaning and Transforming Data...")
    for i, chunk in enumerate(reader):
        initial_chunk_count = len(chunk)
        excluded_stats["initial_total_records"] += initial_chunk_count
        
        # A. Data Integrity: Missing values in critical columns
        chunk = chunk.dropna(subset=['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        excluded_stats["missing_values"] += (initial_chunk_count - len(chunk))
        
        # B. Data Integrity: Duplicates
        count_before_dup = len(chunk)
        chunk = chunk.drop_duplicates()
        excluded_stats["duplicates"] += (count_before_dup - len(chunk))
        
        # C. Normalization: Standardize timestamps
        chunk['tpep_pickup_datetime'] = pd.to_datetime(chunk['tpep_pickup_datetime'], errors='coerce')
        chunk['tpep_dropoff_datetime'] = pd.to_datetime(chunk['tpep_dropoff_datetime'], errors='coerce')
        chunk = chunk.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        
        # D. Data Integrity: Logical Outliers
        # Distance > 0 and < 100 miles
        count_before_dist = len(chunk)
        chunk = chunk[(chunk['trip_distance'] > 0) & (chunk['trip_distance'] < 100)]
        excluded_stats["outliers_distance"] += (count_before_dist - len(chunk))
        
        # Fare > 0 and < 1000
        count_before_fare = len(chunk)
        chunk = chunk[(chunk['fare_amount'] > 0) & (chunk['fare_amount'] < 1000)]
        excluded_stats["outliers_fare"] += (count_before_fare - len(chunk))
        
        # Time consistency: Dropoff after pickup and within reasonable duration (< 6 hours)
        count_before_time = len(chunk)
        chunk['duration_min'] = (chunk['tpep_dropoff_datetime'] - chunk['tpep_pickup_datetime']).dt.total_seconds() / 60
        chunk = chunk[(chunk['duration_min'] > 0) & (chunk['duration_min'] < 360)]
        excluded_stats["outliers_time"] += (count_before_time - len(chunk))
        
        # 2. Feature Engineering
        # Feature 1: Trip Speed (mph) - Insight into traffic conditions
        chunk['trip_speed_mph'] = chunk['trip_distance'] / (chunk['duration_min'] / 60)
        
        # Feature 2: Tip Percentage - Economic insight into customer behavior/satisfaction
        chunk['tip_percentage'] = np.where(chunk['fare_amount'] > 0, (chunk['tip_amount'] / chunk['fare_amount']) * 100, 0)
        
        # Feature 3: Pickup Period (Categorical) - Time-based movement analysis
        def get_period(hour):
            if 5 <= hour < 12: return 'Morning'
            elif 12 <= hour < 17: return 'Afternoon'
            elif 17 <= hour < 21: return 'Evening'
            else: return 'Night'
        
        chunk['pickup_hour'] = chunk['tpep_pickup_datetime'].dt.hour
        chunk['pickup_period'] = chunk['pickup_hour'].apply(get_period)
        
        # 3. Integration: Associate with Zone Lookup Metadata
        # Merge Pickup Location Info
        chunk = chunk.merge(zone_lookup, left_on='PULocationID', right_on='LocationID', how='left')
        chunk = chunk.rename(columns={'Borough': 'PU_Borough', 'Zone': 'PU_Zone', 'service_zone': 'PU_ServiceZone'}).drop('LocationID', axis=1)
        
        # Merge Dropoff Location Info
        chunk = chunk.merge(zone_lookup, left_on='DOLocationID', right_on='LocationID', how='left')
        chunk = chunk.rename(columns={'Borough': 'DO_Borough', 'Zone': 'DO_Zone', 'service_zone': 'DO_ServiceZone'}).drop('LocationID', axis=1)
        
        # Write incrementally to CSV (append mode)
        chunk.to_csv(output_csv, mode='a', header=first_chunk, index=False)
        
        # Write incrementally to Parquet
        if first_chunk:
            chunk.to_parquet(output_parquet, engine='pyarrow', index=False)
            first_chunk = False
        else:
            # Append to existing parquet file
            existing = pd.read_parquet(output_parquet)
            combined = pd.concat([existing, chunk], ignore_index=True)
            combined.to_parquet(output_parquet, engine='pyarrow', index=False)
        
        excluded_stats["final_clean_records"] += len(chunk)
            
        if (i+1) % 10 == 0:
            print(f"Processed {(i+1) * chunk_size} rows... (Clean: {excluded_stats['final_clean_records']})")

    # Save excluded records log
    with open(os.path.join(CLEAN_DIR, LOG_FILE), 'w') as f:
        json.dump(excluded_stats, f, indent=4)
    
    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"Summary:")
    print(f"- Total Raw Records: {excluded_stats['initial_total_records']:,}")
    print(f"- Final Clean Records: {excluded_stats['final_clean_records']:,}")
    print(f"- Excluded (Missing): {excluded_stats['missing_values']:,}")
    print(f"- Excluded (Duplicates): {excluded_stats['duplicates']:,}")
    print(f"- Excluded (Distance Outliers): {excluded_stats['outliers_distance']:,}")
    print(f"- Excluded (Fare Outliers): {excluded_stats['outliers_fare']:,}")
    print(f"- Excluded (Time Outliers): {excluded_stats['outliers_time']:,}")
    print(f"\nFiles saved:")
    print(f"- CSV: {output_csv}")
    print(f"- Parquet: {output_parquet}")
    print(f"- Log: {os.path.join(CLEAN_DIR, LOG_FILE)}")
    print("="*60)

if __name__ == "__main__":
    process_data()
