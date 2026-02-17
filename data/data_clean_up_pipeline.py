"""
Urban Mobility Data Pipeline
============================
Comprehensive pipeline for:
1. Data Integration: Load parquet trip data and associate with taxi zone metadata
2. Data Integrity: Handle missing values, duplicates, and outliers
3. Normalization: Standardize timestamps, numeric fields, and categorical identifiers
4. Feature Engineering: Create derived features for deeper insights
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# =====================================================================
# CONFIGURATION
# =====================================================================

class Config:
    """Pipeline configuration"""
    # Base directory - where the script is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Paths
    RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
    CLEAN_DATA_DIR = os.path.join(BASE_DIR, "clean_data")
    SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
    TAXI_ZONES_DIR = os.path.join(os.path.dirname(BASE_DIR), "taxi_zones")
    
    # Input files
    TRIP_DATA_CSV = os.path.join(RAW_DATA_DIR, "yellow_tripdata_2019-01.csv")
    TRIP_DATA_PARQUET = os.path.join(CLEAN_DATA_DIR, "tripdata.parquet")
    ZONE_LOOKUP_CSV = os.path.join(RAW_DATA_DIR, "taxi_zone_lookup.csv")
    TAXI_ZONES_SHP = os.path.join(TAXI_ZONES_DIR, "taxi_zones.shp")
    
    # Output files
    CLEAN_TRIP_DATA = os.path.join(CLEAN_DATA_DIR, "clean_tripdata_2019-01.csv")
    INTEGRATED_DATA = os.path.join(CLEAN_DATA_DIR, "integrated_trip_data.parquet")
    ZONE_DATA = os.path.join(CLEAN_DATA_DIR, "clean_taxi_zone_data.csv")
    REPORT_FILE = os.path.join(CLEAN_DATA_DIR, "data_quality_report.txt")
    
    # Data quality thresholds
    MAX_TRIP_DISTANCE = 100  # miles
    MIN_TRIP_DISTANCE = 0.01  # miles
    MAX_FARE = 500  # dollars
    MIN_FARE = 2.5  # NYC minimum fare
    MAX_TRIP_DURATION = 180  # minutes
    MIN_TRIP_DURATION = 1  # minute
    MAX_PASSENGER_COUNT = 6
    MIN_PASSENGER_COUNT = 1

# =====================================================================
# STEP 1: DATA INTEGRATION
# =====================================================================

class DataLoader:
    """Load and integrate data from multiple sources"""
    
    @staticmethod
    def convert_csv_to_parquet():
        """Convert CSV to Parquet for efficient processing"""
        print("\n" + "="*70)
        print("STEP 1: DATA CONVERSION (CSV → Parquet)")
        print("="*70)
        
        if os.path.exists(Config.TRIP_DATA_PARQUET):
            print(f"✓ Parquet file already exists: {Config.TRIP_DATA_PARQUET}")
            return
        
        print(f"Converting {Config.TRIP_DATA_CSV} to Parquet format...")
        
        # Read CSV in chunks for memory efficiency
        chunk_size = 100000
        chunks = []
        
        for i, chunk in enumerate(pd.read_csv(Config.TRIP_DATA_CSV, chunksize=chunk_size)):
            chunks.append(chunk)
            if (i + 1) % 10 == 0:
                print(f"  Processed {(i+1)*chunk_size:,} rows...")
        
        df = pd.concat(chunks, ignore_index=True)
        df.to_parquet(Config.TRIP_DATA_PARQUET, engine='pyarrow', compression='snappy')
        
        print(f"✓ Conversion complete: {len(df):,} rows")
        print(f"  Saved to: {Config.TRIP_DATA_PARQUET}")
    
    @staticmethod
    def load_trip_data():
        """Load trip data from Parquet"""
        print("\n" + "="*70)
        print("STEP 2: LOAD TRIP DATA")
        print("="*70)
        
        if not os.path.exists(Config.TRIP_DATA_PARQUET):
            DataLoader.convert_csv_to_parquet()
        
        print(f"Loading trip data from: {Config.TRIP_DATA_PARQUET}")
        df = pd.read_parquet(Config.TRIP_DATA_PARQUET)
        
        print(f"✓ Loaded {len(df):,} trip records")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return df
    
    @staticmethod
    def load_zone_lookup():
        """Load taxi zone lookup table"""
        print("\n" + "="*70)
        print("STEP 3: LOAD TAXI ZONE LOOKUP")
        print("="*70)
        
        print(f"Loading zone lookup from: {Config.ZONE_LOOKUP_CSV}")
        zones = pd.read_csv(Config.ZONE_LOOKUP_CSV)
        
        print(f"✓ Loaded {len(zones)} taxi zones")
        print(f"  Boroughs: {zones['Borough'].unique().tolist()}")
        print(f"  Service zones: {zones['service_zone'].unique().tolist()}")
        
        return zones
    
    @staticmethod
    def load_zone_geometry():
        """Load taxi zone spatial data (optional)"""
        print("\n" + "="*70)
        print("STEP 4: LOAD TAXI ZONE GEOMETRY (OPTIONAL)")
        print("="*70)
        
        if not HAS_GEOPANDAS:
            print(f"⚠ Geopandas not installed - skipping spatial data")
            return None
        
        if not os.path.exists(Config.TAXI_ZONES_SHP):
            print(f"⚠ Shapefile not found: {Config.TAXI_ZONES_SHP}")
            return None
        
        try:
            print(f"Loading shapefile from: {Config.TAXI_ZONES_SHP}")
            gdf = gpd.read_file(Config.TAXI_ZONES_SHP)
            print(f"✓ Loaded {len(gdf)} zone geometries")
            print(f"  CRS: {gdf.crs}")
            return gdf
        except Exception as e:
            print(f"⚠ Error loading shapefile: {e}")
            return None
    
    @staticmethod
    def integrate_data(trips_df, zones_df):
        """Associate trip data with zone metadata"""
        print("\n" + "="*70)
        print("STEP 5: DATA INTEGRATION")
        print("="*70)
        
        print("Merging trip data with pickup zone information...")
        trips_df = trips_df.merge(
            zones_df,
            left_on='PULocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_pickup')
        )
        trips_df.rename(columns={
            'Borough': 'pickup_borough',
            'Zone': 'pickup_zone',
            'service_zone': 'pickup_service_zone'
        }, inplace=True)
        
        print("Merging trip data with dropoff zone information...")
        trips_df = trips_df.merge(
            zones_df,
            left_on='DOLocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_dropoff')
        )
        trips_df.rename(columns={
            'Borough': 'dropoff_borough',
            'Zone': 'dropoff_zone',
            'service_zone': 'dropoff_service_zone'
        }, inplace=True)
        
        # Remove duplicate LocationID columns
        if 'LocationID' in trips_df.columns:
            trips_df.drop(columns=['LocationID'], inplace=True)
        if 'LocationID_dropoff' in trips_df.columns:
            trips_df.drop(columns=['LocationID_dropoff'], inplace=True)
        
        print(f"✓ Integration complete: {len(trips_df):,} records")
        print(f"  New columns: pickup_borough, pickup_zone, dropoff_borough, dropoff_zone")
        
        return trips_df

# =====================================================================
# STEP 2: DATA INTEGRITY
# =====================================================================

class DataCleaner:
    """Handle missing values, duplicates, and outliers"""
    
    def __init__(self):
        self.report = []
    
    def handle_missing_values(self, df):
        """Identify and resolve missing values"""
        print("\n" + "="*70)
        print("STEP 6: HANDLE MISSING VALUES")
        print("="*70)
        
        initial_rows = len(df)
        missing_summary = df.isnull().sum()
        missing_pct = (missing_summary / len(df) * 100).round(2)
        
        print("Missing values by column:")
        for col in df.columns:
            if missing_summary[col] > 0:
                print(f"  {col}: {missing_summary[col]} ({missing_pct[col]}%)")
        
        self.report.append(f"Missing Values Analysis:\n")
        self.report.append(f"Initial rows: {initial_rows:,}\n")
        
        # Strategy 1: Drop rows with missing critical fields
        critical_fields = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                          'PULocationID', 'DOLocationID', 'trip_distance', 'fare_amount']
        
        for field in critical_fields:
            if field in df.columns:
                before = len(df)
                df = df.dropna(subset=[field])
                dropped = before - len(df)
                if dropped > 0:
                    print(f"  Dropped {dropped} rows with missing {field}")
                    self.report.append(f"  Dropped {dropped} rows: missing {field}\n")
        
        # Strategy 2: Fill missing passenger_count with median
        if 'passenger_count' in df.columns and df['passenger_count'].isnull().any():
            median_passengers = df['passenger_count'].median()
            null_count = df['passenger_count'].isnull().sum()
            df['passenger_count'].fillna(median_passengers, inplace=True)
            print(f"  Filled {null_count} missing passenger_count with median: {median_passengers}")
            self.report.append(f"  Filled {null_count} passenger_count with median: {median_passengers}\n")
        
        # Strategy 3: Fill missing payment-related fields with 0
        payment_fields = ['extra', 'mta_tax', 'tip_amount', 'tolls_amount', 
                         'improvement_surcharge', 'congestion_surcharge']
        for field in payment_fields:
            if field in df.columns and df[field].isnull().any():
                null_count = df[field].isnull().sum()
                df[field].fillna(0, inplace=True)
                print(f"  Filled {null_count} missing {field} with 0")
                self.report.append(f"  Filled {null_count} {field} with 0\n")
        
        final_rows = len(df)
        print(f"✓ Missing value handling complete: {final_rows:,} rows remaining")
        self.report.append(f"Final rows after missing value handling: {final_rows:,}\n\n")
        
        return df
    
    def remove_duplicates(self, df):
        """Identify and remove duplicate records"""
        print("\n" + "="*70)
        print("STEP 7: REMOVE DUPLICATES")
        print("="*70)
        
        initial_rows = len(df)
        
        # Define duplicate criteria: same pickup/dropoff time, locations, and fare
        duplicate_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                         'PULocationID', 'DOLocationID', 'fare_amount']
        
        # Check for exact duplicates
        duplicates = df.duplicated(subset=duplicate_cols, keep='first').sum()
        
        if duplicates > 0:
            df = df.drop_duplicates(subset=duplicate_cols, keep='first')
            print(f"  Removed {duplicates} duplicate records")
            self.report.append(f"Duplicates Removed: {duplicates}\n")
        else:
            print("  No duplicates found")
            self.report.append("Duplicates Removed: 0\n")
        
        final_rows = len(df)
        print(f"✓ Duplicate removal complete: {final_rows:,} rows remaining")
        self.report.append(f"Rows after duplicate removal: {final_rows:,}\n\n")
        
        return df
    
    def detect_outliers(self, df):
        """Identify physical and logical outliers"""
        print("\n" + "="*70)
        print("STEP 8: DETECT AND HANDLE OUTLIERS")
        print("="*70)
        
        initial_rows = len(df)
        self.report.append("Outlier Detection:\n")
        
        # 1. Trip distance outliers
        print("\n1. Trip Distance Outliers:")
        distance_outliers = (
            (df['trip_distance'] < Config.MIN_TRIP_DISTANCE) | 
            (df['trip_distance'] > Config.MAX_TRIP_DISTANCE)
        )
        outlier_count = distance_outliers.sum()
        print(f"   Found {outlier_count} trips with invalid distance")
        print(f"   Range: {df['trip_distance'].min():.2f} - {df['trip_distance'].max():.2f} miles")
        df = df[~distance_outliers]
        self.report.append(f"  Distance outliers removed: {outlier_count}\n")
        
        # 2. Fare amount outliers
        print("\n2. Fare Amount Outliers:")
        fare_outliers = (
            (df['fare_amount'] < Config.MIN_FARE) | 
            (df['fare_amount'] > Config.MAX_FARE)
        )
        outlier_count = fare_outliers.sum()
        print(f"   Found {outlier_count} trips with invalid fare")
        print(f"   Range: ${df['fare_amount'].min():.2f} - ${df['fare_amount'].max():.2f}")
        df = df[~fare_outliers]
        self.report.append(f"  Fare outliers removed: {outlier_count}\n")
        
        # 3. Passenger count outliers
        print("\n3. Passenger Count Outliers:")
        passenger_outliers = (
            (df['passenger_count'] < Config.MIN_PASSENGER_COUNT) | 
            (df['passenger_count'] > Config.MAX_PASSENGER_COUNT)
        )
        outlier_count = passenger_outliers.sum()
        print(f"   Found {outlier_count} trips with invalid passenger count")
        df = df[~passenger_outliers]
        self.report.append(f"  Passenger count outliers removed: {outlier_count}\n")
        
        # 4. Temporal outliers (trip duration)
        print("\n4. Temporal Outliers:")
        df['trip_duration_minutes'] = (
            pd.to_datetime(df['tpep_dropoff_datetime']) - 
            pd.to_datetime(df['tpep_pickup_datetime'])
        ).dt.total_seconds() / 60
        
        temporal_outliers = (
            (df['trip_duration_minutes'] < Config.MIN_TRIP_DURATION) | 
            (df['trip_duration_minutes'] > Config.MAX_TRIP_DURATION)
        )
        outlier_count = temporal_outliers.sum()
        print(f"   Found {outlier_count} trips with invalid duration")
        print(f"   Range: {df['trip_duration_minutes'].min():.2f} - {df['trip_duration_minutes'].max():.2f} minutes")
        df = df[~temporal_outliers]
        self.report.append(f"  Temporal outliers removed: {outlier_count}\n")
        
        # 5. Logical outliers (dropoff before pickup)
        print("\n5. Logical Outliers:")
        logical_outliers = df['trip_duration_minutes'] < 0
        outlier_count = logical_outliers.sum()
        if outlier_count > 0:
            print(f"   Found {outlier_count} trips where dropoff < pickup")
            df = df[~logical_outliers]
            self.report.append(f"  Logical outliers removed: {outlier_count}\n")
        else:
            print(f"   No logical inconsistencies found")
        
        # 6. Total amount validation
        print("\n6. Total Amount Validation:")
        df['calculated_total'] = (
            df['fare_amount'] + df['extra'] + df['mta_tax'] + 
            df['tip_amount'] + df['tolls_amount'] + 
            df['improvement_surcharge'] + df['congestion_surcharge'].fillna(0)
        )
        
        # Allow 1% tolerance for rounding
        total_mismatch = abs(df['total_amount'] - df['calculated_total']) > 0.5
        outlier_count = total_mismatch.sum()
        print(f"   Found {outlier_count} trips with total amount mismatch")
        df = df[~total_mismatch]
        self.report.append(f"  Total amount mismatches removed: {outlier_count}\n")
        
        df.drop(columns=['calculated_total'], inplace=True)
        
        final_rows = len(df)
        removed = initial_rows - final_rows
        print(f"\n✓ Outlier detection complete:")
        print(f"  Initial: {initial_rows:,} rows")
        print(f"  Removed: {removed:,} outliers ({removed/initial_rows*100:.2f}%)")
        print(f"  Final: {final_rows:,} rows")
        
        self.report.append(f"\nTotal outliers removed: {removed:,} ({removed/initial_rows*100:.2f}%)\n")
        self.report.append(f"Final rows: {final_rows:,}\n\n")
        
        return df
    
    def save_report(self):
        """Save data quality report"""
        with open(Config.REPORT_FILE, 'w') as f:
            f.write("DATA QUALITY REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.writelines(self.report)
        
        print(f"\n✓ Data quality report saved to: {Config.REPORT_FILE}")

# =====================================================================
# STEP 3: NORMALIZATION
# =====================================================================

class DataNormalizer:
    """Standardize timestamps, numeric fields, and categorical identifiers"""
    
    @staticmethod
    def normalize_timestamps(df):
        """Standardize all timestamp fields"""
        print("\n" + "="*70)
        print("STEP 9: NORMALIZE TIMESTAMPS")
        print("="*70)
        
        timestamp_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        
        for col in timestamp_cols:
            if col in df.columns:
                print(f"  Converting {col} to datetime...")
                df[col] = pd.to_datetime(df[col])
                
                # Extract useful temporal components
                if col == 'tpep_pickup_datetime':
                    df['pickup_year'] = df[col].dt.year
                    df['pickup_month'] = df[col].dt.month
                    df['pickup_day'] = df[col].dt.day
                    df['pickup_hour'] = df[col].dt.hour
                    df['pickup_dayofweek'] = df[col].dt.dayofweek  # 0=Monday, 6=Sunday
                    df['pickup_is_weekend'] = df['pickup_dayofweek'].isin([5, 6]).astype(int)
        
        print(f"✓ Timestamp normalization complete")
        print(f"  Added temporal features: year, month, day, hour, dayofweek, is_weekend")
        
        return df
    
    @staticmethod
    def normalize_numeric_fields(df):
        """Standardize numeric fields for database storage"""
        print("\n" + "="*70)
        print("STEP 10: NORMALIZE NUMERIC FIELDS")
        print("="*70)
        
        # Round numeric fields to appropriate precision
        numeric_precision = {
            'trip_distance': 2,
            'fare_amount': 2,
            'extra': 2,
            'mta_tax': 2,
            'tip_amount': 2,
            'tolls_amount': 2,
            'improvement_surcharge': 2,
            'total_amount': 2,
            'congestion_surcharge': 2,
            'trip_duration_minutes': 2
        }
        
        for col, precision in numeric_precision.items():
            if col in df.columns:
                df[col] = df[col].round(precision)
                print(f"  Rounded {col} to {precision} decimal places")
        
        # Ensure integer fields are proper integers
        integer_fields = ['VendorID', 'passenger_count', 'RatecodeID', 
                         'PULocationID', 'DOLocationID', 'payment_type']
        
        for col in integer_fields:
            if col in df.columns:
                df[col] = df[col].astype(int)
                print(f"  Converted {col} to integer")
        
        print(f"✓ Numeric field normalization complete")
        
        return df
    
    @staticmethod
    def normalize_categorical_fields(df):
        """Standardize categorical identifiers"""
        print("\n" + "="*70)
        print("STEP 11: NORMALIZE CATEGORICAL FIELDS")
        print("="*70)
        
        # Standardize store_and_fwd_flag
        if 'store_and_fwd_flag' in df.columns:
            df['store_and_fwd_flag'] = df['store_and_fwd_flag'].str.upper()
            print(f"  Standardized store_and_fwd_flag to uppercase")
        
        # Standardize zone names (strip whitespace, title case)
        zone_cols = ['pickup_borough', 'pickup_zone', 'pickup_service_zone',
                    'dropoff_borough', 'dropoff_zone', 'dropoff_service_zone']
        
        for col in zone_cols:
            if col in df.columns:
                df[col] = df[col].str.strip()
                print(f"  Standardized {col}")
        
        # Create categorical codes for efficient storage
        categorical_mappings = {}
        
        for col in ['pickup_borough', 'dropoff_borough']:
            if col in df.columns:
                df[col] = df[col].astype('category')
                categorical_mappings[col] = dict(enumerate(df[col].cat.categories))
        
        print(f"✓ Categorical field normalization complete")
        
        return df, categorical_mappings

# =====================================================================
# STEP 4: FEATURE ENGINEERING
# =====================================================================

class FeatureEngineer:
    """Create derived features for deeper insights"""
    
    @staticmethod
    def create_derived_features(df):
        """Define and create meaningful derived features"""
        print("\n" + "="*70)
        print("STEP 12: FEATURE ENGINEERING")
        print("="*70)
        
        print("\nCreating derived features...\n")
        
        # ===================================================================
        # FEATURE 1: Average Speed (mph)
        # ===================================================================
        print("1. AVERAGE SPEED (mph)")
        print("   Justification: Measures traffic flow and congestion patterns.")
        print("   Formula: trip_distance / (trip_duration_minutes / 60)")
        
        df['avg_speed_mph'] = np.where(
            df['trip_duration_minutes'] > 0,
            df['trip_distance'] / (df['trip_duration_minutes'] / 60),
            0
        )
        
        # Cap unrealistic speeds (>80 mph in NYC)
        df['avg_speed_mph'] = df['avg_speed_mph'].clip(upper=80)
        df['avg_speed_mph'] = df['avg_speed_mph'].round(2)
        
        print(f"   Range: {df['avg_speed_mph'].min():.2f} - {df['avg_speed_mph'].max():.2f} mph")
        print(f"   Mean: {df['avg_speed_mph'].mean():.2f} mph")
        print(f"   ✓ Feature created\n")
        
        # ===================================================================
        # FEATURE 2: Cost Per Mile ($/mile)
        # ===================================================================
        print("2. COST PER MILE ($/mile)")
        print("   Justification: Economic efficiency metric for riders and pricing analysis.")
        print("   Formula: total_amount / trip_distance")
        
        df['cost_per_mile'] = np.where(
            df['trip_distance'] > 0,
            df['total_amount'] / df['trip_distance'],
            0
        )
        df['cost_per_mile'] = df['cost_per_mile'].round(2)
        
        print(f"   Range: ${df['cost_per_mile'].min():.2f} - ${df['cost_per_mile'].max():.2f}")
        print(f"   Mean: ${df['cost_per_mile'].mean():.2f}")
        print(f"   ✓ Feature created\n")
        
        # ===================================================================
        # FEATURE 3: Tip Percentage
        # ===================================================================
        print("3. TIP PERCENTAGE (%)")
        print("   Justification: Measures customer satisfaction and driver service quality.")
        print("   Formula: (tip_amount / fare_amount) * 100")
        
        df['tip_percentage'] = np.where(
            df['fare_amount'] > 0,
            (df['tip_amount'] / df['fare_amount']) * 100,
            0
        )
        df['tip_percentage'] = df['tip_percentage'].clip(upper=100).round(2)
        
        print(f"   Range: {df['tip_percentage'].min():.2f}% - {df['tip_percentage'].max():.2f}%")
        print(f"   Mean: {df['tip_percentage'].mean():.2f}%")
        print(f"   ✓ Feature created\n")
        
        # ===================================================================
        # FEATURE 4: Time of Day Category
        # ===================================================================
        print("4. TIME OF DAY CATEGORY")
        print("   Justification: Captures demand patterns across different times.")
        print("   Categories: Night(0-6), Morning Rush(6-10), Midday(10-16),")
        print("               Evening Rush(16-20), Night(20-24)")
        
        def categorize_time_of_day(hour):
            if 0 <= hour < 6:
                return 'Night'
            elif 6 <= hour < 10:
                return 'Morning Rush'
            elif 10 <= hour < 16:
                return 'Midday'
            elif 16 <= hour < 20:
                return 'Evening Rush'
            else:
                return 'Night'
        
        df['time_of_day'] = df['pickup_hour'].apply(categorize_time_of_day)
        
        print(f"   Distribution:")
        for cat, count in df['time_of_day'].value_counts().items():
            print(f"     {cat}: {count:,} ({count/len(df)*100:.1f}%)")
        print(f"   ✓ Feature created\n")
        
        # ===================================================================
        # FEATURE 5: Inter-Borough Trip Flag
        # ===================================================================
        print("5. INTER-BOROUGH TRIP FLAG")
        print("   Justification: Identifies trips crossing borough boundaries,")
        print("                  useful for urban mobility and pricing analysis.")
        print("   Formula: pickup_borough != dropoff_borough")
        
        df['is_inter_borough'] = (
            df['pickup_borough'] != df['dropoff_borough']
        ).astype(int)
        
        inter_borough_count = df['is_inter_borough'].sum()
        inter_borough_pct = inter_borough_count / len(df) * 100
        
        print(f"   Inter-borough trips: {inter_borough_count:,} ({inter_borough_pct:.1f}%)")
        print(f"   Intra-borough trips: {len(df) - inter_borough_count:,} ({100-inter_borough_pct:.1f}%)")
        print(f"   ✓ Feature created\n")
        
        # ===================================================================
        # FEATURE 6: Revenue Per Minute ($/min)
        # ===================================================================
        print("6. REVENUE PER MINUTE ($/min)")
        print("   Justification: Driver profitability metric - earnings efficiency.")
        print("   Formula: total_amount / trip_duration_minutes")
        
        df['revenue_per_minute'] = np.where(
            df['trip_duration_minutes'] > 0,
            df['total_amount'] / df['trip_duration_minutes'],
            0
        )
        df['revenue_per_minute'] = df['revenue_per_minute'].round(2)
        
        print(f"   Range: ${df['revenue_per_minute'].min():.2f} - ${df['revenue_per_minute'].max():.2f}")
        print(f"   Mean: ${df['revenue_per_minute'].mean():.2f}/min")
        print(f"   ✓ Feature created\n")
        
        print("="*70)
        print(f"✓ Feature engineering complete: 6 derived features created")
        print("="*70)
        
        return df

# =====================================================================
# MAIN PIPELINE EXECUTION
# =====================================================================

class DataPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.cleaner = DataCleaner()
        
        # Ensure output directory exists
        os.makedirs(Config.CLEAN_DATA_DIR, exist_ok=True)
    
    def run(self):
        """Execute the complete data pipeline"""
        print("\n" + "="*70)
        print("NYC TAXI DATA PIPELINE")
        print("="*70)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            # ====== DATA INTEGRATION ======
            loader = DataLoader()
            
            # Load raw data
            trips_df = loader.load_trip_data()
            zones_df = loader.load_zone_lookup()
            geo_df = loader.load_zone_geometry()
            
            # Integrate data sources
            trips_df = loader.integrate_data(trips_df, zones_df)
            
            # ====== DATA INTEGRITY ======
            trips_df = self.cleaner.handle_missing_values(trips_df)
            trips_df = self.cleaner.remove_duplicates(trips_df)
            trips_df = self.cleaner.detect_outliers(trips_df)
            
            # ====== NORMALIZATION ======
            normalizer = DataNormalizer()
            trips_df = normalizer.normalize_timestamps(trips_df)
            trips_df = normalizer.normalize_numeric_fields(trips_df)
            trips_df, categorical_mappings = normalizer.normalize_categorical_fields(trips_df)
            
            # ====== FEATURE ENGINEERING ======
            engineer = FeatureEngineer()
            trips_df = engineer.create_derived_features(trips_df)
            
            # ====== SAVE RESULTS ======
            self.save_results(trips_df, zones_df)
            
            # ====== GENERATE REPORT ======
            self.cleaner.save_report()
            self.print_summary(trips_df)
            
            # ====== COMPLETION ======
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            print("\n" + "="*70)
            print("PIPELINE COMPLETE")
            print("="*70)
            print(f"Start Time:    {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"End Time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration:      {duration:.2f} seconds")
            print(f"Final Records: {len(trips_df):,}")
            print("="*70)
            
            return trips_df
            
        except Exception as e:
            print(f"\n❌ ERROR: Pipeline failed with exception:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_results(self, trips_df, zones_df):
        """Save cleaned and integrated data"""
        print("\n" + "="*70)
        print("STEP 13: SAVE RESULTS")
        print("="*70)
        
        # Save integrated trip data as Parquet (efficient format)
        print(f"\n1. Saving integrated trip data...")
        trips_df.to_parquet(Config.INTEGRATED_DATA, engine='pyarrow', compression='snappy')
        file_size = os.path.getsize(Config.INTEGRATED_DATA) / 1024**2
        print(f"   ✓ Saved to: {Config.INTEGRATED_DATA}")
        print(f"   Size: {file_size:.2f} MB")
        
        # Save cleaned trip data as CSV (for compatibility)
        print(f"\n2. Saving clean trip data (CSV)...")
        trips_df.to_csv(Config.CLEAN_TRIP_DATA, index=False)
        file_size = os.path.getsize(Config.CLEAN_TRIP_DATA) / 1024**2
        print(f"   ✓ Saved to: {Config.CLEAN_TRIP_DATA}")
        print(f"   Size: {file_size:.2f} MB")
        
        # Save zone data
        print(f"\n3. Saving zone data...")
        zones_df.to_csv(Config.ZONE_DATA, index=False)
        print(f"   ✓ Saved to: {Config.ZONE_DATA}")
        
        print(f"\n✓ All results saved successfully")
    
    def print_summary(self, df):
        """Print pipeline summary statistics"""
        print("\n" + "="*70)
        print("DATA SUMMARY")
        print("="*70)
        
        print(f"\nDataset Overview:")
        print(f"  Total Records: {len(df):,}")
        print(f"  Total Columns: {len(df.columns)}")
        print(f"  Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print(f"\nTrip Statistics:")
        print(f"  Avg Distance: {df['trip_distance'].mean():.2f} miles")
        print(f"  Avg Duration: {df['trip_duration_minutes'].mean():.2f} minutes")
        print(f"  Avg Fare: ${df['fare_amount'].mean():.2f}")
        print(f"  Avg Speed: {df['avg_speed_mph'].mean():.2f} mph")
        
        print(f"\nEconomic Metrics:")
        print(f"  Avg Cost/Mile: ${df['cost_per_mile'].mean():.2f}")
        print(f"  Avg Tip: ${df['tip_amount'].mean():.2f} ({df['tip_percentage'].mean():.1f}%)")
        print(f"  Avg Revenue/Minute: ${df['revenue_per_minute'].mean():.2f}")
        
        print(f"\nTop Pickup Boroughs:")
        for borough, count in df['pickup_borough'].value_counts().head(5).items():
            print(f"  {borough}: {count:,} trips ({count/len(df)*100:.1f}%)")
        
        print(f"\nDerived Features Created:")
        derived_features = ['avg_speed_mph', 'cost_per_mile', 'tip_percentage', 
                           'time_of_day', 'is_inter_borough', 'revenue_per_minute']
        for feature in derived_features:
            if feature in df.columns:
                print(f"  ✓ {feature}")

# =====================================================================
# RUN PIPELINE
# =====================================================================

if __name__ == "__main__":
    pipeline = DataPipeline()
    result_df = pipeline.run() 