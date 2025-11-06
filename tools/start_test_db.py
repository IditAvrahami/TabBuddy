#!/usr/bin/env python3
"""
Script to start a PostgreSQL test database using Docker.
Run this before running tests to ensure a clean test database is available.
"""

import subprocess
import time
import psycopg2
import sys

def start_test_db():
    """Start PostgreSQL test database using Docker"""
    print("Starting PostgreSQL test database...")
    
    # Check if container already exists
    result = subprocess.run([
        "docker", "ps", "-a", "--filter", "name=tabbuddy-test-db", "--format", "{{.Names}}"
    ], capture_output=True, text=True)
    
    if "tabbuddy-test-db" in result.stdout:
        print("Removing existing test container...")
        subprocess.run(["docker", "rm", "-f", "tabbuddy-test-db"], check=False)
    
    # Start PostgreSQL container
    print("Starting new PostgreSQL container...")
    subprocess.run([
        "docker", "run", "-d",
        "--name", "tabbuddy-test-db",
        "-e", "POSTGRES_USER=postgres",
        "-e", "POSTGRES_PASSWORD=postgres",
        "-e", "POSTGRES_DB=tabbuddy_test",
        "-p", "5434:5432",
        "postgres:16"
    ], check=True)
    
    # Wait for database to be ready
    print("Waiting for PostgreSQL to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5434,
                user="postgres",
                password="postgres",
                database="tabbuddy_test"
            )
            conn.close()
            print("✅ PostgreSQL test database is ready!")
            print("Database URL: postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test")
            return True
        except psycopg2.OperationalError as e:
            if i == max_retries - 1:
                print(f"❌ Failed to connect to test database: {e}")
                return False
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(1)
    
    return False

def stop_test_db():
    """Stop PostgreSQL test database"""
    print("Stopping PostgreSQL test database...")
    subprocess.run(["docker", "stop", "tabbuddy-test-db"], check=False)
    subprocess.run(["docker", "rm", "tabbuddy-test-db"], check=False)
    print("✅ Test database stopped and removed")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_test_db()
    else:
        if start_test_db():
            print("\nTo stop the test database, run: python tools/start_test_db.py stop")
        else:
            sys.exit(1)

