#!/usr/bin/env python3
"""
Create a drug with notification for the current UTC time to test immediately.
"""

import requests
import json
from datetime import datetime, date, time, timedelta

API_BASE = "http://127.0.0.1:8000"
TODAY = date.today().isoformat()

def create_utc_notification():
    """Create a drug that will trigger notification at the current UTC time."""
    
    # Get current UTC time
    utc_now = datetime.utcnow()
    utc_time = utc_now.strftime("%H:%M")
    
    drug_payload = {
        "name": f"UTC Test {utc_now.strftime('%H%M%S')}",
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": TODAY,
        "end_date": TODAY,
        "dependency_type": "absolute",
        "absolute_time": utc_time
    }
    
    print(f"Creating drug with notification at: {utc_time} UTC")
    print(f"Current UTC time: {utc_now.strftime('%H:%M:%S')}")
    print("The notification should appear immediately!")
    
    try:
        response = requests.post(f"{API_BASE}/drug", json=drug_payload)
        if response.status_code == 200:
            print("✅ Drug created successfully!")
            print("🔄 Test the notifications API now")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_utc_notification()
