# NYC Taxi Data Analysis Pipeline

Complete analysis pipeline for NYC Yellow Taxi trip data with memory-efficient batch processing.

## Quick Start

### 1. Run Complete Analysis
Execute all analysis modules in one command:
```bash
python3 run_full_analysis.py
```

This will run:
- Data quality verification
- Temporal analysis (hourly, daily patterns)
- Spatial analysis (geographic patterns)
- Economic analysis (revenue, pricing)
- Operational analysis (performance metrics)
- Visualization generation

**Output:** All results saved to `analysis_results/` directory

### 2. Configuration Options

Edit `run_full_analysis.py` at the top to customize:

```python
DATA_SOURCE = 'new-clean-dataset/clean_tripdata.parquet'
SKIP_VERIFICATION = False  # Set True to skip verification (faster)
RUN_VISUALIZATIONS = True  # Set False to skip visualizations
```

### 3. Verify Data Quality

Run data verification separately:
```bash
python3 verify_data.py
```

**Configure mode** in the script (line 9):
- `MODE = 'sample'` - Fast (1000 records)
- `MODE = 'full'` - Complete dataset with batch processing

## File Cleanup

### Preview what can be deleted:
```bash
python3 cleanup_files.py --dry-run
```

### Actually delete unnecessary files:
```bash
python3 cleanup_files.py --confirm
```

This removes:
- Duplicate/obsolete scripts
- Original raw data (already processed)
- Log files and checkpoints
- Compressed archives

**Saves ~656 MB of space!**

## Project Structure

### Essential Files (Keep These):
```
run_full_analysis.py      - Master script to run all analyses
process_data_safe.py      - Data cleaning with batch processing
verify_data.py            - Data quality verification
analyze_temporal.py       - Time-based pattern analysis
analyze_spatial.py        - Geographic pattern analysis
analyze_economic.py       - Revenue and pricing analysis
analyze_operational.py    - Performance metrics analysis
generate_visualizations.py - Create charts and graphs
cleanup_files.py          - Remove unnecessary files
```

### Output Directories:
```
analysis_results/         - All analysis outputs (JSON + visualizations)
new-clean-dataset/        - Cleaned data (CSV + Parquet)
```

### Obsolete Files (Can Delete):
```
analyze_data_part1.py     - Replaced by modular scripts
analyze_data_part2.py     - Replaced by modular scripts
process_data.py           - Replaced by process_data_safe.py
process_data_fast.py      - Replaced by process_data_safe.py
convert_to_parquet.py     - One-time conversion (no longer needed)
yellow_tripdata_2019-01.csv - Original data (already processed)
```

## Memory Management

All scripts use **batch processing** to handle large datasets (15M+ records) without crashing:

- **Batch Size:** 100,000 records per chunk
- **Memory Cleanup:** Explicit memory release after each batch
- **Progress Tracking:** Status updates during processing

## Typical Workflow

1. **Initial Setup:**
   ```bash
   # Process raw data (if not done yet)
   python3 process_data_safe.py
   ```

2. **Run Full Analysis:**
   ```bash
   # Execute complete analysis pipeline
   python3 run_full_analysis.py
   ```

3. **Check Results:**
   ```bash
   # View generated files
   ls -lh analysis_results/
   ```

4. **Cleanup (Optional):**
   ```bash
   # Remove unnecessary files
   python3 cleanup_files.py --confirm
   ```

## Analysis Outputs

### JSON Files:
- `temporal_analysis.json` - Hourly/daily patterns
- `spatial_analysis.json` - Geographic insights
- `economic_analysis.json` - Revenue analysis
- `operational_analysis.json` - Performance metrics
- `execution_log.json` - Pipeline execution details

### Visualizations:
- Charts and graphs in `analysis_results/visualizations/`

## Troubleshooting

**Out of memory errors?**
- Reduce `BATCH_SIZE` in analysis scripts (default: 100,000)
- Set `MODE = 'sample'` in verify_data.py
- Close other applications

**Script fails?**
- Check `analysis_results/execution_log.json` for error details
- Ensure data files exist in `new-clean-dataset/`
- Verify Python packages are installed

**Need faster execution?**
- Set `SKIP_VERIFICATION = True` in run_full_analysis.py
- Set `RUN_VISUALIZATIONS = False` if charts not needed

## Requirements

```bash
pip install pandas pyarrow numpy matplotlib seaborn
```

---

**Dataset:** NYC Yellow Taxi Trip Data (January 2019)  
**Records:** 15M+ trips  
**Processing:** Memory-efficient batch processing  
**Output Format:** JSON + visualizations
