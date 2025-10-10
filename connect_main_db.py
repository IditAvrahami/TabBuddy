#!/usr/bin/env python3
"""
Script to connect to the main application database using pgcli.
This assumes the main database is running via docker-compose.
"""

import subprocess
import sys
import os

def connect_to_main_db():
    """Connect to main database using pgcli"""
    print("🔍 Setting up main database connection...")
    
    # Check if main database is running
    result = subprocess.run([
        "docker", "ps", "--filter", "name=tabbuddy-db", "--format", "{{.Names}}"
    ], capture_output=True, text=True)
    
    if "tabbuddy-db" not in result.stdout:
        print("📦 Starting main database...")
        print("   Run: docker-compose up -d db")
        print("   Or:  docker run -d --name tabbuddy-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tabbuddy -p 5432:5432 postgres:16")
        sys.exit(1)
    else:
        print("✅ Main database is running")
    
    # Database connection details
    db_url = "postgresql://postgres@localhost:5432/tabbuddy"
    
    print("🚀 Connecting to main database with pgcli...")
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
    connect_to_main_db()
