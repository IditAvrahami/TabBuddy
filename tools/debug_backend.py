#!/usr/bin/env python3
"""
Debug the backend notification logic step by step.
"""

import requests
import json
from datetime import datetime, date, time

API_BASE = "http://127.0.0.1:8000"
TODAY = date.today().isoformat()

def debug_backend():
    """Debug the backend notification logic."""

    print("🔍 Debugging backend notification logic...")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Today's date: {TODAY}")

    # 1. Check all drugs
    print("\n1. Checking all drugs...")
    try:
        response = requests.get(f"{API_BASE}/drug")
        if response.status_code == 200:
            drugs = response.json()
            print(f"✅ Found {len(drugs)} drugs:")
            for drug in drugs:
                print(f"   - {drug['name']} (ID: {drug['id']})")
                print(f"     Start: {drug['start_date']}, End: {drug.get('end_date', 'None')}")
                print(f"     Type: {drug['dependency_type']}, Time: {drug.get('absolute_time', 'None')}")
        else:
            print(f"❌ Failed to get drugs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting drugs: {e}")

    # 2. Check notifications with different time windows
    print("\n2. Testing notification time windows...")
    now = datetime.now()

    # Test with a drug scheduled for right now
    test_time = now.strftime("%H:%M")
    drug_payload = {
        "name": f"Debug Test {now.strftime('%H%M%S')}",
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": TODAY,
        "end_date": TODAY,
        "dependency_type": "absolute",
        "absolute_time": test_time
    }

    print(f"Creating test drug for: {test_time}")
    try:
        response = requests.post(f"{API_BASE}/drug", json=drug_payload)
        if response.status_code == 200:
            print("✅ Test drug created")
        else:
            print(f"❌ Failed to create test drug: {response.text}")
    except Exception as e:
        print(f"❌ Error creating test drug: {e}")

    # 3. Check notifications again
    print("\n3. Checking notifications after creating test drug...")
    try:
        response = requests.get(f"{API_BASE}/notifications?day={TODAY}")
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Found {len(notifications)} notifications:")
            for notif in notifications:
                print(f"   - {notif['drug_name']} at {notif['scheduled_time']}")
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")

    # 4. Test with a drug scheduled 1 minute ago (should definitely show)
    print("\n4. Creating drug for 1 minute ago...")
    past_time = (now.replace(second=0, microsecond=0) - datetime.timedelta(minutes=1)).strftime("%H:%M")
    drug_payload2 = {
        "name": f"Past Test {now.strftime('%H%M%S')}",
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": TODAY,
        "end_date": TODAY,
        "dependency_type": "absolute",
        "absolute_time": past_time
    }

    print(f"Creating drug for: {past_time} (1 minute ago)")
    try:
        response = requests.post(f"{API_BASE}/drug", json=drug_payload2)
        if response.status_code == 200:
            print("✅ Past test drug created")
        else:
            print(f"❌ Failed to create past test drug: {response.text}")
    except Exception as e:
        print(f"❌ Error creating past test drug: {e}")

    # 5. Check notifications again
    print("\n5. Final notification check...")
    try:
        response = requests.get(f"{API_BASE}/notifications?day={TODAY}")
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Found {len(notifications)} notifications:")
            for notif in notifications:
                print(f"   - {notif['drug_name']} at {notif['scheduled_time']}")
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")

if __name__ == "__main__":
    debug_backend()
