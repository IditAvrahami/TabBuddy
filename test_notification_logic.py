#!/usr/bin/env python3
"""
Test the notification logic to see what should be showing.
"""

import requests
import json
from datetime import datetime, date

API_BASE = "http://127.0.0.1:8000"
TODAY = date.today().isoformat()

def test_notification_logic():
    """Test what notifications should be showing."""
    
    print("🔍 Testing notification logic...")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Today's date: {TODAY}")
    
    try:
        # Get notifications
        response = requests.get(f"{API_BASE}/notifications?day={TODAY}")
        if response.status_code == 200:
            notifications = response.json()
            print(f"\n✅ Found {len(notifications)} notifications:")
            
            now = datetime.now()
            due_count = 0
            
            for notif in notifications:
                scheduled_time = datetime.fromisoformat(notif['scheduled_time'].replace('Z', '+00:00'))
                time_diff = (scheduled_time - now).total_seconds() / 60  # minutes
                
                status = "DUE NOW" if time_diff <= 0 else f"in {time_diff:.1f} min"
                if time_diff <= 0:
                    due_count += 1
                
                print(f"   - {notif['drug_name']} at {scheduled_time.strftime('%H:%M')} ({status})")
            
            print(f"\n📊 Summary:")
            print(f"   Total notifications: {len(notifications)}")
            print(f"   Due now: {due_count}")
            print(f"   Should show modal: {'YES' if due_count > 0 else 'NO'}")
            
            if due_count > 0:
                print(f"\n🎯 The modal should be showing {due_count} notification(s)!")
                print("   If you don't see it, the issue is in the frontend.")
            else:
                print(f"\n⏰ No notifications are due yet.")
                print("   Create a drug for the current time to test.")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_notification_logic()
