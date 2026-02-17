import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import gc
import os
from datetime import datetime

print("=" * 70)
print("CONVERTING CSV TO PARQUET FORMAT")
print("=" * 70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

csv_file = "new-clean-dataset/clean_tripdata.csv"
parquet_file = "new-clean-dataset/clean_tripdata.parquet"

# Remove old parquet if exists
if os.path.exists(parquet_file):
    os.remove(parquet_file)
    print(f"Removed existing parquet file\n")

print(f"Reading CSV: {csv_file}")
print(f"Writing to: {parquet_file}\n")

# First, determine consistent dtypes by sampling the file
print("Determining schema...")
sample = pd.read_csv(csv_file, nrows=10000)

# Force consistent dtypes for problematic columns
dtype_spec = {}
for col in sample.columns:
    if sample[col].dtype in ['int64', 'float64']:
        # Check if column can be float
        dtype_spec[col] = 'float64'  # Use float64 for numeric consistency
    else:
        dtype_spec[col] = sample[col].dtype

print(f"Schema established from sample\n")

# Convert in chunks with consistent dtypes
chunk_size = 100000
reader = pd.read_csv(csv_file, chunksize=chunk_size, dtype=dtype_spec)

parquet_writer = None
total_rows = 0

for i, chunk in enumerate(reader):
    table = pa.Table.from_pandas(chunk, preserve_index=False)
    
    if parquet_writer is None:
        # Create writer on first chunk
        parquet_writer = pq.ParquetWriter(parquet_file, table.schema)
        print(f"Created ParquetWriter with consistent schema")
    
    parquet_writer.write_table(table)
    total_rows += len(chunk)
    
    if (i + 1) % 10 == 0:
        print(f"  Converted {total_rows:,} rows...")
    
    del chunk, table
    gc.collect()

if parquet_writer:
    parquet_writer.close()

print(f"\n✓ Conversion complete!")
print(f"  Total rows: {total_rows:,}")
print(f"  Output: {parquet_file}")
print(f"  Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
