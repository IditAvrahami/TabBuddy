#!/usr/bin/env python3
"""
Script to connect to the test database using pgcli for real-time data inspection.
This will start the test database if it's not running and then connect with pgcli.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.start_test_db import start_test_db, stop_test_db

def connect_to_test_db():
    """Connect to test database using pgcli"""
    print("🔍 Setting up database connection...")
    
    # Check if test database is already running
    result = subprocess.run([
        "docker", "ps", "--filter", "name=tabbuddy-test-db", "--format", "{{.Names}}"
    ], capture_output=True, text=True)
    
    if "tabbuddy-test-db" not in result.stdout:
        print("📦 Starting test database...")
        if not start_test_db():
            print("❌ Failed to start test database")
            sys.exit(1)
    else:
        print("✅ Test database is already running")
    
    # Database connection details
    db_url = "postgresql://postgres:postgres@localhost:5434/tabbuddy_test"
    
    print("🚀 Connecting to test database with pgcli...")
    print("💡 Useful commands:")
    print("   - \\dt                    : List all tables")
    print("   - \\d drugs              : Describe drugs table structure")
    print("   - SELECT * FROM drugs;   : View all drugs")
    print("   - \\q                    : Quit pgcli")
    print("   - \\?                    : Show help")
    print()
    
    try:
        # Connect with pgcli using python -m
        subprocess.run([
            "python", "-m", "pgcli", db_url
        ])
    except KeyboardInterrupt:
        print("\n👋 Disconnected from database")
    except FileNotFoundError:
        print("❌ pgcli not found. Please install it first:")
        print("   pip install pgcli")
        sys.exit(1)

if __name__ == "__main__":
    connect_to_test_db()

