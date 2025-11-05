#!/usr/bin/env python3
"""
Test script to create a drug with absolute time notification for today.
This will help you see the notification modal in action.
"""

import requests
import json
from datetime import datetime, date, time

# Configuration
API_BASE = "http://127.0.0.1:8000"
TODAY = date.today().isoformat()

def create_test_drug():
    """Create a drug with absolute time for today to trigger notification."""
    
    # Create a drug that should trigger a notification
    # Set the time to 1 minute from now for immediate testing
    now = datetime.now()
    test_time = now.replace(second=0, microsecond=0)
    if now.minute < 59:
        test_time = test_time.replace(minute=now.minute + 1)
    else:
        test_time = test_time.replace(hour=now.hour + 1, minute=0)
    
    drug_payload = {
        "name": "Test Notification Drug",
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": TODAY,
        "end_date": TODAY,  # Only for today
        "dependency_type": "absolute",
        "absolute_time": test_time.strftime("%H:%M")
    }
    
    print(f"Creating test drug with absolute time: {test_time.strftime('%H:%M')}")
    print(f"Today's date: {TODAY}")
    
    try:
        # Create the drug
        response = requests.post(f"{API_BASE}/drug", json=drug_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Drug created successfully: {result}")
            
            # Check notifications
            print("\nChecking notifications...")
            notif_response = requests.get(f"{API_BASE}/notifications?day={TODAY}")
            if notif_response.status_code == 200:
                notifications = notif_response.json()
                print(f"📋 Notifications for today: {len(notifications)}")
                for notif in notifications:
                    print(f"  - {notif['drug_name']} at {notif['scheduled_time']}")
            else:
                print(f"❌ Failed to get notifications: {notif_response.status_code}")
                
        else:
            print(f"❌ Failed to create drug: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the backend is running:")
        print("   docker-compose up backend")
    except Exception as e:
        print(f"❌ Error: {e}")

def cleanup_test_drugs():
    """Clean up test drugs."""
    try:
        # Get all drugs
        response = requests.get(f"{API_BASE}/drug")
        if response.status_code == 200:
            drugs = response.json()
            test_drugs = [d for d in drugs if "Test Notification" in d["name"]]
            
            for drug in test_drugs:
                print(f"Deleting test drug: {drug['name']}")
                del_response = requests.delete(f"{API_BASE}/drug/{drug['id']}")
                if del_response.status_code == 200:
                    print(f"✅ Deleted {drug['name']}")
                else:
                    print(f"❌ Failed to delete {drug['name']}")
        else:
            print(f"❌ Failed to get drugs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        print("🧹 Cleaning up test drugs...")
        cleanup_test_drugs()
    else:
        print("🧪 Creating test notification drug...")
        print("This will create a drug with absolute time for today.")
        print("The frontend should show a notification modal when you refresh the page.")
        print("\nTo clean up test drugs later, run: python test_notification.py cleanup")
        print()
        create_test_drug()
