#!/usr/bin/env python3
"""
Master Analysis Script - NYC Taxi Data
======================================
This script orchestrates the complete data analysis pipeline.
It runs all analysis modules sequentially and generates comprehensive results.

Usage:
    python3 run_full_analysis.py

Configuration:
    - Set DATA_SOURCE to specify which dataset to analyze
    - Set SKIP_VERIFICATION to skip data validation (faster)
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
DATA_SOURCE = 'new-clean-dataset/clean_tripdata.parquet'  # Path to dataset
SKIP_VERIFICATION = False  # Set True to skip data verification
RUN_VISUALIZATIONS = True  # Set False to skip visualization generation
# ============================================================

print("=" * 80)
print("NYC TAXI DATA - COMPLETE ANALYSIS PIPELINE")
print("=" * 80)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Data Source: {DATA_SOURCE}")
print("=" * 80)
print()

# Track execution times and results
execution_log = {
    "start_time": datetime.now().isoformat(),
    "data_source": DATA_SOURCE,
    "steps": [],
    "errors": []
}

def run_script(script_name, description):
    """Execute a Python script and track its execution"""
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*80}")
    
    step_start = time.time()
    step_info = {
        "script": script_name,
        "description": description,
        "start_time": datetime.now().isoformat()
    }
    
    try:
        # Check if script exists
        if not os.path.exists(script_name):
            print(f"⚠ WARNING: {script_name} not found. Skipping...")
            step_info["status"] = "skipped"
            step_info["message"] = "File not found"
            execution_log["steps"].append(step_info)
            return False
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per script
        )
        
        step_duration = time.time() - step_start
        
        # Display output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n✓ Completed successfully in {step_duration:.2f} seconds")
            step_info["status"] = "success"
            step_info["duration_seconds"] = step_duration
            execution_log["steps"].append(step_info)
            return True
        else:
            print(f"\n✗ Failed with exit code {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            step_info["status"] = "failed"
            step_info["exit_code"] = result.returncode
            step_info["error"] = result.stderr[:500]  # Limit error message size
            execution_log["steps"].append(step_info)
            execution_log["errors"].append({
                "script": script_name,
                "error": result.stderr[:500]
            })
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n✗ Timeout: Script exceeded 10 minute limit")
        step_info["status"] = "timeout"
        step_info["message"] = "Exceeded 10 minute timeout"
        execution_log["steps"].append(step_info)
        execution_log["errors"].append({
            "script": script_name,
            "error": "Timeout after 10 minutes"
        })
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        step_info["status"] = "error"
        step_info["error"] = str(e)
        execution_log["steps"].append(step_info)
        execution_log["errors"].append({
            "script": script_name,
            "error": str(e)
        })
        return False

# ============================================================
# PIPELINE EXECUTION
# ============================================================

# Step 0: Verify data (optional)
if not SKIP_VERIFICATION:
    if os.path.exists('verify_data.py'):
        run_script('verify_data.py', 'Data Quality Verification')
    else:
        print("\n⚠ Skipping verification - verify_data.py not found")

# Step 1: Temporal Analysis
run_script('analyze_temporal.py', 'Temporal Analysis (Time-based patterns)')

# Step 2: Spatial Analysis
run_script('analyze_spatial.py', 'Spatial Analysis (Geographic patterns)')

# Step 3: Economic Analysis
run_script('analyze_economic.py', 'Economic Analysis (Revenue & pricing)')

# Step 4: Operational Analysis
run_script('analyze_operational.py', 'Operational Analysis (Performance metrics)')

# Step 5: Generate Visualizations (optional)
if RUN_VISUALIZATIONS:
    if os.path.exists('generate_visualizations.py'):
        run_script('generate_visualizations.py', 'Visualization Generation')
    else:
        print("\n⚠ Skipping visualizations - generate_visualizations.py not found")

# ============================================================
# SUMMARY & RESULTS
# ============================================================

execution_log["end_time"] = datetime.now().isoformat()
total_duration = time.time() - time.mktime(datetime.fromisoformat(execution_log["start_time"]).timetuple())
execution_log["total_duration_seconds"] = total_duration

print("\n" + "=" * 80)
print("ANALYSIS PIPELINE COMPLETE")
print("=" * 80)

# Count successes and failures
successful = sum(1 for step in execution_log["steps"] if step.get("status") == "success")
failed = sum(1 for step in execution_log["steps"] if step.get("status") == "failed")
skipped = sum(1 for step in execution_log["steps"] if step.get("status") == "skipped")

print(f"\nExecution Summary:")
print(f"  ✓ Successful: {successful}")
print(f"  ✗ Failed:     {failed}")
print(f"  ⊘ Skipped:    {skipped}")
print(f"  ⏱ Total Time: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")

if execution_log["errors"]:
    print(f"\n⚠ {len(execution_log['errors'])} error(s) occurred:")
    for error in execution_log["errors"]:
        print(f"  - {error['script']}: {error['error'][:100]}...")

# Save execution log
log_file = 'analysis_results/execution_log.json'
os.makedirs('analysis_results', exist_ok=True)
with open(log_file, 'w') as f:
    json.dump(execution_log, f, indent=2)
print(f"\nExecution log saved to: {log_file}")

# List generated results
print(f"\nGenerated Results:")
if os.path.exists('analysis_results'):
    for file in sorted(os.listdir('analysis_results')):
        file_path = os.path.join('analysis_results', file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/1024**2:.1f} MB"
            print(f"  - {file:<40} ({size_str})")

print("\n" + "=" * 80)
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if failed == 0 else 1)
