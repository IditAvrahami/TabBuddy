#!/usr/bin/env python3
"""
Script to run tests with automatic test database setup.
"""

import subprocess
import sys
import os
from start_test_db import start_test_db, stop_test_db

def run_tests():
    """Run tests with test database"""
    print("🚀 Setting up test environment...")
    
    # Start test database
    if not start_test_db():
        print("❌ Failed to start test database")
        sys.exit(1)
    
    try:
        # Set test database URL
        os.environ["TEST_DATABASE_URL"] = "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test"
        
        print("🧪 Running tests...")
        result = subprocess.run([
            "python", "-m", "pytest", "-v", "backend/test/"
        ])
        
        return result.returncode == 0
        
    finally:
        print("🧹 Cleaning up test database...")
        stop_test_db()

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
