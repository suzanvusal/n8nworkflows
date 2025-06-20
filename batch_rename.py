#!/usr/bin/env python3
"""
Batch Workflow Renamer - Process workflows in controlled batches
"""

import subprocess
import sys
import time
from pathlib import Path

def run_batch_rename(pattern: str, batch_size: int = 50, start_from: int = 0):
    """Run workflow renaming in controlled batches."""
    
    print(f"Starting batch rename for pattern: {pattern}")
    print(f"Batch size: {batch_size}")
    print(f"Starting from batch: {start_from}")
    print("=" * 60)
    
    # First, get total count
    result = subprocess.run([
        "python3", "workflow_renamer.py", 
        "--pattern", pattern, 
        "--report-only"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error getting report: {result.stderr}")
        return False
    
    # Extract total count from output
    lines = result.stdout.split('\n')
    total_files = 0
    for line in lines:
        if "Total files to rename:" in line:
            total_files = int(line.split(':')[1].strip())
            break
    
    if total_files == 0:
        print("No files found to rename.")
        return True
    
    print(f"Total files to process: {total_files}")
    
    # Calculate batches
    total_batches = (total_files + batch_size - 1) // batch_size
    
    if start_from >= total_batches:
        print(f"Start batch {start_from} is beyond total batches {total_batches}")
        return False
    
    print(f"Will process {total_batches - start_from} batches")
    
    # Process each batch
    success_count = 0
    error_count = 0
    
    for batch_num in range(start_from, total_batches):
        print(f"\n--- Batch {batch_num + 1}/{total_batches} ---")
        
        # Create a temporary script that processes only this batch
        batch_script = f"""
import sys
sys.path.append('.')
from workflow_renamer import WorkflowRenamer
import os

renamer = WorkflowRenamer(dry_run=False)
rename_plan = renamer.plan_renames(['{pattern}'])

# Process only this batch
start_idx = {batch_num * batch_size}
end_idx = min({(batch_num + 1) * batch_size}, len(rename_plan))
batch_plan = rename_plan[start_idx:end_idx]

print(f"Processing {{len(batch_plan)}} files in this batch...")

if batch_plan:
    results = renamer.execute_renames(batch_plan)
    print(f"Batch results: {{results['success']}} successful, {{results['errors']}} errors")
else:
    print("No files to process in this batch")
"""
        
        # Write temporary script
        with open('temp_batch.py', 'w') as f:
            f.write(batch_script)
        
        try:
            # Execute batch
            result = subprocess.run(["python3", "temp_batch.py"], 
                                  capture_output=True, text=True, timeout=300)
            
            print(result.stdout)
            if result.stderr:
                print(f"Warnings: {result.stderr}")
            
            if result.returncode == 0:
                # Count successes from output
                for line in result.stdout.split('\n'):
                    if "successful," in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            success_count += int(parts[1])
                        break
            else:
                print(f"Batch {batch_num + 1} failed: {result.stderr}")
                error_count += batch_size
            
        except subprocess.TimeoutExpired:
            print(f"Batch {batch_num + 1} timed out")
            error_count += batch_size
        except Exception as e:
            print(f"Error in batch {batch_num + 1}: {str(e)}")
            error_count += batch_size
        finally:
            # Clean up temp file
            if os.path.exists('temp_batch.py'):
                os.remove('temp_batch.py')
        
        # Small pause between batches
        time.sleep(1)
    
    print(f"\n" + "=" * 60)
    print(f"BATCH PROCESSING COMPLETE")
    print(f"Total successful renames: {success_count}")
    print(f"Total errors: {error_count}")
    
    return error_count == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_rename.py <pattern> [batch_size] [start_from]")
        print("Examples:")
        print("  python3 batch_rename.py generic_workflow")
        print("  python3 batch_rename.py generic_workflow 25")
        print("  python3 batch_rename.py generic_workflow 25 5")
        sys.exit(1)
    
    pattern = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    # Confirm before proceeding
    print(f"About to rename workflows with pattern: {pattern}")
    print(f"Batch size: {batch_size}")
    print(f"Starting from batch: {start_from}")
    
    response = input("\nProceed? (y/N): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    success = run_batch_rename(pattern, batch_size, start_from)
    
    if success:
        print("\nAll batches completed successfully!")
    else:
        print("\nSome batches had errors. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()