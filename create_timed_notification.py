#!/usr/bin/env python3
"""
Create a drug with notification for the exact current time to test proper timing.
"""

import requests
import json
from datetime import datetime, date, time, timedelta

API_BASE = "http://127.0.0.1:8000"
TODAY = date.today().isoformat()

def create_timed_notification():
    """Create a drug that will trigger notification at the exact current UTC time."""
    
    # Set time to current UTC time
    now = datetime.utcnow()
    current_time = now.strftime("%H:%M")
    
    drug_payload = {
        "name": f"Timed Test {now.strftime('%H%M')}",
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": TODAY,
        "end_date": TODAY,
        "dependency_type": "absolute",
        "absolute_time": current_time
    }
    
    print(f"Creating drug with notification at: {current_time} UTC")
    print(f"Current UTC time: {now.strftime('%H:%M:%S')}")
    print("The notification should appear within 5 minutes!")
    
    try:
        response = requests.post(f"{API_BASE}/drug", json=drug_payload)
        if response.status_code == 200:
            print("✅ Drug created successfully!")
            print("🔄 Refresh your browser at http://localhost:3000")
            print("⏰ The modal should appear within 5 minutes of the scheduled time")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_timed_notification()
