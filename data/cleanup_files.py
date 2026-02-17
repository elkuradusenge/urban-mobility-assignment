#!/usr/bin/env python3
"""
Cleanup Script - Remove unnecessary files
==========================================
This script identifies and optionally removes files that are not needed
for the core analysis pipeline.

Usage:
    python3 cleanup_files.py --dry-run    # See what would be deleted
    python3 cleanup_files.py --confirm    # Actually delete the files
"""

import os
import sys
import argparse
from datetime import datetime

def get_file_size(filepath):
    """Get human-readable file size"""
    size = os.path.getsize(filepath)
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size/1024:.1f} KB"
    elif size < 1024**3:
        return f"{size/1024**2:.1f} MB"
    else:
        return f"{size/1024**3:.2f} GB"

def scan_files():
    """Scan directory and categorize files"""
    
    # Define categories
    categories = {
        "duplicate_scripts": [],
        "old_datasets": [],
        "log_files": [],
        "checkpoints": [],
        "zip_files": [],
        "keep": []
    }
    
    # Files to potentially remove
    duplicate_candidates = [
        'process_data.py',  # Keep process_data_safe.py instead
        'process_data_fast.py',  # Keep process_data_safe.py instead
        'analyze_data_part1.py',  # Replaced by modular scripts
        'analyze_data_part2.py',  # Replaced by modular scripts
        'convert_to_parquet.py',  # One-time conversion, no longer needed
    ]
    
    old_data_candidates = [
        'yellow_tripdata_2019-01.csv',  # Original raw data (already processed)
        'taxi_zone_lookup.csv',  # Duplicate (exists in old-original/)
    ]
    
    # Scan current directory
    for item in os.listdir('.'):
        if item.startswith('.'):
            continue
            
        filepath = os.path.join('.', item)
        
        if not os.path.isfile(filepath):
            continue
        
        # Categorize
        if item in duplicate_candidates:
            categories["duplicate_scripts"].append(filepath)
        elif item in old_data_candidates:
            categories["old_datasets"].append(filepath)
        elif item.endswith('.log'):
            categories["log_files"].append(filepath)
        elif item.endswith('checkpoint.json'):
            categories["checkpoints"].append(filepath)
        elif item.endswith('.zip'):
            categories["zip_files"].append(filepath)
        else:
            categories["keep"].append(filepath)
    
    return categories

def main():
    parser = argparse.ArgumentParser(description='Clean up unnecessary files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--confirm', action='store_true',
                       help='Actually delete the files')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.confirm:
        print("ERROR: Must specify either --dry-run or --confirm")
        print("\nUsage:")
        print("  python3 cleanup_files.py --dry-run     # Preview what will be deleted")
        print("  python3 cleanup_files.py --confirm     # Actually delete files")
        sys.exit(1)
    
    print("=" * 80)
    print("FILE CLEANUP ANALYSIS")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (no files will be deleted)' if args.dry_run else 'CONFIRM (files will be deleted)'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    categories = scan_files()
    
    # Display what will be removed
    total_size = 0
    files_to_remove = []
    
    print("FILES RECOMMENDED FOR REMOVAL:")
    print("-" * 80)
    
    if categories["duplicate_scripts"]:
        print("\n1. DUPLICATE/OBSOLETE SCRIPTS:")
        print("   (Replaced by newer, memory-efficient versions)")
        for filepath in categories["duplicate_scripts"]:
            size = get_file_size(filepath)
            print(f"   - {filepath:<50} {size:>10}")
            files_to_remove.append(filepath)
            total_size += os.path.getsize(filepath)
    
    if categories["old_datasets"]:
        print("\n2. ORIGINAL RAW DATA FILES:")
        print("   (Already processed and saved in new-clean-dataset/)")
        for filepath in categories["old_datasets"]:
            size = get_file_size(filepath)
            print(f"   - {filepath:<50} {size:>10}")
            files_to_remove.append(filepath)
            total_size += os.path.getsize(filepath)
    
    if categories["log_files"]:
        print("\n3. LOG FILES:")
        for filepath in categories["log_files"]:
            size = get_file_size(filepath)
            print(f"   - {filepath:<50} {size:>10}")
            files_to_remove.append(filepath)
            total_size += os.path.getsize(filepath)
    
    if categories["checkpoints"]:
        print("\n4. CHECKPOINT FILES:")
        for filepath in categories["checkpoints"]:
            size = get_file_size(filepath)
            print(f"   - {filepath:<50} {size:>10}")
            files_to_remove.append(filepath)
            total_size += os.path.getsize(filepath)
    
    if categories["zip_files"]:
        print("\n5. COMPRESSED ARCHIVES:")
        print("   (Contents already extracted)")
        for filepath in categories["zip_files"]:
            size = get_file_size(filepath)
            print(f"   - {filepath:<50} {size:>10}")
            files_to_remove.append(filepath)
            total_size += os.path.getsize(filepath)
    
    print("\n" + "-" * 80)
    print(f"Total files to remove: {len(files_to_remove)}")
    print(f"Total space to recover: {get_file_size('') if total_size == 0 else get_file_size(str(total_size)) if total_size < 1024 else (f'{total_size/1024:.1f} KB' if total_size < 1024**2 else f'{total_size/1024**2:.1f} MB' if total_size < 1024**3 else f'{total_size/1024**3:.2f} GB')}")
    
    # Files to keep
    print("\n" + "=" * 80)
    print("ESSENTIAL FILES TO KEEP:")
    print("-" * 80)
    
    essential_files = [
        'run_full_analysis.py',
        'analyze_temporal.py',
        'analyze_spatial.py',
        'analyze_economic.py',
        'analyze_operational.py',
        'process_data_safe.py',
        'verify_data.py',
        'generate_visualizations.py',
    ]
    
    for filepath in essential_files:
        if os.path.exists(filepath):
            size = get_file_size(filepath)
            print(f"  ✓ {filepath:<50} {size:>10}")
    
    # Execute deletion if confirmed
    if args.confirm and files_to_remove:
        print("\n" + "=" * 80)
        print("EXECUTING CLEANUP...")
        print("-" * 80)
        
        deleted = 0
        failed = 0
        
        for filepath in files_to_remove:
            try:
                os.remove(filepath)
                print(f"  ✓ Deleted: {filepath}")
                deleted += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {filepath}: {e}")
                failed += 1
        
        print("-" * 80)
        print(f"Deleted: {deleted} files")
        if failed > 0:
            print(f"Failed: {failed} files")
    
    elif args.dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN COMPLETE - No files were deleted")
        print("Run with --confirm to actually delete these files")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
