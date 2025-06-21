#!/usr/bin/env python3
"""
Script to clean up the database by removing orphaned workflows
(workflows that exist in database but not on filesystem)
"""

import os
import sqlite3
from pathlib import Path

def cleanup_orphaned_workflows():
    """Remove workflow entries from database that don't have corresponding files."""
    
    # Connect to database
    db_path = "workflows.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the API server first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all workflow filenames from database
        cursor.execute("SELECT filename FROM workflows")
        db_workflows = [row[0] for row in cursor.fetchall()]
        
        # Get all actual workflow files from filesystem
        workflows_dir = Path("workflows")
        if not workflows_dir.exists():
            print("❌ Workflows directory not found.")
            return
        
        actual_files = set()
        for file_path in workflows_dir.glob("*.json"):
            actual_files.add(file_path.name)
        
        # Find orphaned workflows (in database but not on filesystem)
        orphaned = []
        for db_filename in db_workflows:
            if db_filename not in actual_files:
                orphaned.append(db_filename)
        
        if not orphaned:
            print("✅ No orphaned workflows found. Database is clean!")
            return
        
        print(f"🧹 Found {len(orphaned)} orphaned workflows in database:")
        for i, filename in enumerate(orphaned[:10], 1):  # Show first 10
            print(f"  {i}. {filename}")
        
        if len(orphaned) > 10:
            print(f"  ... and {len(orphaned) - 10} more")
        
        # Ask for confirmation
        response = input(f"\n❓ Remove {len(orphaned)} orphaned workflows from database? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Operation cancelled.")
            return
        
        # Remove orphaned workflows
        placeholders = ','.join(['?' for _ in orphaned])
        cursor.execute(f"DELETE FROM workflows WHERE filename IN ({placeholders})", orphaned)
        
        # Also remove from FTS table
        cursor.execute(f"DELETE FROM workflows_fts WHERE filename IN ({placeholders})", orphaned)
        
        conn.commit()
        print(f"✅ Removed {len(orphaned)} orphaned workflows from database.")
        
        # Show updated stats
        cursor.execute("SELECT COUNT(*) FROM workflows")
        total_count = cursor.fetchone()[0]
        print(f"📊 Database now contains {total_count} workflows.")
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        conn.rollback()
    finally:
        conn.close()

def find_missing_workflows():
    """Find workflow files that exist on filesystem but not in database."""
    
    db_path = "workflows.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the API server first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all workflow filenames from database
        cursor.execute("SELECT filename FROM workflows")
        db_workflows = set(row[0] for row in cursor.fetchall())
        
        # Get all actual workflow files from filesystem
        workflows_dir = Path("workflows")
        if not workflows_dir.exists():
            print("❌ Workflows directory not found.")
            return
        
        actual_files = []
        for file_path in workflows_dir.glob("*.json"):
            actual_files.append(file_path.name)
        
        # Find missing workflows (on filesystem but not in database)
        missing = []
        for filename in actual_files:
            if filename not in db_workflows:
                missing.append(filename)
        
        if not missing:
            print("✅ All workflow files are indexed in database!")
            return
        
        print(f"📁 Found {len(missing)} workflow files not in database:")
        for i, filename in enumerate(missing[:10], 1):  # Show first 10
            print(f"  {i}. {filename}")
        
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        
        print(f"\n💡 Run 'curl -X POST http://localhost:8000/api/reindex?force=true' to reindex all workflows.")
        
    except Exception as e:
        print(f"❌ Error checking for missing workflows: {e}")
    finally:
        conn.close()

def show_database_stats():
    """Show current database statistics."""
    
    db_path = "workflows.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the API server first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get total workflows
        cursor.execute("SELECT COUNT(*) FROM workflows")
        total = cursor.fetchone()[0]
        
        # Get active/inactive counts
        cursor.execute("SELECT COUNT(*) FROM workflows WHERE active = 1")
        active = cursor.fetchone()[0]
        inactive = total - active
        
        # Get trigger type distribution
        cursor.execute("SELECT trigger_type, COUNT(*) FROM workflows GROUP BY trigger_type ORDER BY COUNT(*) DESC")
        triggers = cursor.fetchall()
        
        # Show filesystem stats
        workflows_dir = Path("workflows")
        if workflows_dir.exists():
            actual_files = len(list(workflows_dir.glob("*.json")))
        else:
            actual_files = 0
        
        print("📊 Database Statistics:")
        print(f"  Total workflows in DB: {total}")
        print(f"  Active workflows: {active}")
        print(f"  Inactive workflows: {inactive}")
        print(f"  Files on filesystem: {actual_files}")
        
        if total != actual_files:
            print(f"  ⚠️  Database/filesystem mismatch: {abs(total - actual_files)} difference")
        
        print("\n🎯 Trigger Types:")
        for trigger_type, count in triggers:
            print(f"  {trigger_type}: {count}")
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "cleanup":
            cleanup_orphaned_workflows()
        elif command == "missing":
            find_missing_workflows()
        elif command == "stats":
            show_database_stats()
        else:
            print("❌ Unknown command. Use: cleanup, missing, or stats")
    else:
        print("🧹 Database Cleanup Tool")
        print("\nAvailable commands:")
        print("  python3 cleanup_database.py cleanup  - Remove orphaned workflows from database")
        print("  python3 cleanup_database.py missing  - Find workflows missing from database")
        print("  python3 cleanup_database.py stats    - Show database statistics")
        print("\nRunning stats by default...\n")
        show_database_stats() 