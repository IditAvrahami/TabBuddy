from datetime import date, time
from freezegun import freeze_time

from fastapi.testclient import TestClient


def create_absolute_payload(name: str, hhmm: str, start: str, end: str | None = None):
    payload = {
        "name": name,
        "kind": "pill",
        "amount_per_dose": 1,
        "frequency_per_day": 1,
        "start_date": start,
        "end_date": end,
        "dependency_type": "absolute",
        "absolute_time": hhmm,
    }
    return payload


@freeze_time("2025-10-26 20:00:00")
def test_notifications_returns_absolute_within_range(test_client: TestClient):
    # Arrange: create an absolute schedule valid today with time very close to now
    today = date.today().isoformat()
    from datetime import datetime, timedelta
    now = datetime.now()
    # Create a notification that's due right now (within the 5-minute window)
    future_time_dt = now
    future_time = future_time_dt.strftime("%H:%M")
    payload = create_absolute_payload("AbsDrug", future_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # Act
    resp = test_client.get("/notifications")

    # Assert
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    item = items[0]
    assert item["drug_name"] == "AbsDrug"
    assert item["dependency_type"] == "absolute"
    assert item["scheduled_time"].endswith(f"{future_time}:00")


@freeze_time("2025-10-26 20:00:00")
def test_notifications_snooze(test_client: TestClient):
    """Test that snoozing a notification works correctly"""
    today = date.today().isoformat()
    # Use current time (exactly now) to ensure it's within the 5-minute window
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("SnoozeDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "SnoozeDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # snooze 30 minutes
    snooze = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 30})
    assert snooze.status_code == 200

    # After snoozing, notification should disappear (it's now 30 minutes in the future)
    notif_after_snooze = test_client.get("/notifications").json()
    assert len(notif_after_snooze) == 0


@freeze_time("2025-10-26 20:00:00")
def test_notifications_dismiss(test_client: TestClient):
    """Test that dismissing a notification works correctly"""
    today = date.today().isoformat()
    # Use current time (exactly now) to ensure it's within the 5-minute window
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("DismissDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "DismissDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # dismiss notification
    dismiss = test_client.post(f"/notifications/{sid}/dismiss")
    assert dismiss.status_code == 200

    # now notifications should be empty (dismissed)
    notif_after_dismiss = test_client.get("/notifications").json()
    assert len(notif_after_dismiss) == 0


@freeze_time("2025-10-26 20:00:00")
def test_notifications_snooze_reappears_after_time(test_client: TestClient):
    """Test that snoozed notifications pop up again after snooze time expires"""
    today = date.today().isoformat()
    # Create a notification that's due right now (within the 5-minute window)
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("SnoozeReappearDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "SnoozeReappearDrug")
    sid = schedule["id"]

    # Check notification appears initially (it's due now)
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # snooze for 10 minutes
    snooze = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 10})
    assert snooze.status_code == 200

    # After snoozing, notification should disappear (it's now 10 minutes in the future)
    notif_after_snooze = test_client.get("/notifications").json()
    assert len(notif_after_snooze) == 0

    # Fast forward time by 10 minutes to when snooze expires
    with freeze_time("2025-10-26 20:10:00"):
        # Now the notification should reappear because snooze time has expired
        notif_after_snooze_expires = test_client.get("/notifications").json()
        assert len(notif_after_snooze_expires) == 1
        assert notif_after_snooze_expires[0]["drug_name"] == "SnoozeReappearDrug"


@freeze_time("2025-10-26 20:00:00")
def test_notifications_snooze_multiple_reappearances(test_client: TestClient):
    """Test that notifications can be snoozed multiple times and reappear each time"""
    today = date.today().isoformat()
    # Create a notification that's due right now
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("MultiSnoozeDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "MultiSnoozeDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # First snooze for 10 minutes (20:00 + 10 = 20:10)
    snooze1 = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 10})
    assert snooze1.status_code == 200
    notif_after_snooze1 = test_client.get("/notifications").json()
    assert len(notif_after_snooze1) == 0

    # Fast forward 10 minutes - notification should reappear
    with freeze_time("2025-10-26 20:10:00"):
        notif_reappear1 = test_client.get("/notifications").json()
        assert len(notif_reappear1) == 1

        # Snooze again for 20 minutes (should now be 20:10 + 20 = 20:30)
        snooze2 = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 20})
        assert snooze2.status_code == 200
        notif_after_snooze2 = test_client.get("/notifications").json()
        assert len(notif_after_snooze2) == 0

    # Fast forward to 20:30 (20 minutes past the new snooze time) - notification should reappear again
    with freeze_time("2025-10-26 20:30:00"):
        notif_reappear2 = test_client.get("/notifications").json()
        assert len(notif_reappear2) == 1
        assert notif_reappear2[0]["drug_name"] == "MultiSnoozeDrug"


def test_notifications_returns_empty_out_of_range(test_client: TestClient):
    # Arrange: create schedule for tomorrow
    today = date.today()
    tomorrow = date.fromordinal(today.toordinal() + 1).isoformat()
    payload = create_absolute_payload("TomorrowDrug", "10:00", tomorrow, tomorrow)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # Act: request notifications for today
    resp = test_client.get("/notifications")
    assert resp.status_code == 200
    assert resp.json() == []


def test_notifications_none_after_delete(test_client: TestClient):
    # Arrange
    today = date.today().isoformat()
    payload = create_absolute_payload("ToDelete", "08:30", today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch created schedules and delete the schedule id returned by list API
    list_resp = test_client.get("/drug")
    assert list_resp.status_code == 200
    found = next(d for d in list_resp.json() if d["name"] == "ToDelete")
    schedule_id = found["id"]

    del_resp = test_client.delete(f"/drug/{schedule_id}")
    assert del_resp.status_code == 200

    # Act
    resp = test_client.get("/notifications")
    assert resp.status_code == 200
    assert resp.json() == []


@freeze_time("2025-10-26 20:00:00")
def test_notifications_snooze_multiple_times(test_client: TestClient):
    """Test that snoozing multiple times works correctly"""
    today = date.today().isoformat()
    # Use a time that's due right now (within 5-minute window)
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("MultiSnoozeDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "MultiSnoozeDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # First snooze: 15 minutes
    snooze1 = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 15})
    assert snooze1.status_code == 200

    # After first snooze, notification should disappear
    notif1 = test_client.get("/notifications").json()
    assert len(notif1) == 0

    # Second snooze: 30 minutes (should update the snooze time)
    snooze2 = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 30})
    assert snooze2.status_code == 200

    # After second snooze, notification should still be gone
    notif2 = test_client.get("/notifications").json()
    assert len(notif2) == 0


@freeze_time("2025-10-26 20:00:00")
def test_notifications_snooze_then_dismiss(test_client: TestClient):
    """Test that dismissing a snoozed notification works correctly"""
    today = date.today().isoformat()
    # Use a time that's due right now (within 5-minute window)
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("SnoozeThenDismissDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "SnoozeThenDismissDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # Snooze first
    snooze = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 45})
    assert snooze.status_code == 200

    # After snoozing, notification should disappear
    notif_after_snooze = test_client.get("/notifications").json()
    assert len(notif_after_snooze) == 0

    # Then dismiss
    dismiss = test_client.post(f"/notifications/{sid}/dismiss")
    assert dismiss.status_code == 200

    # Verify dismiss worked (should still be empty)
    notif2 = test_client.get("/notifications").json()
    assert len(notif2) == 0


@freeze_time("2025-10-26 20:00:00")
def test_notifications_dismiss_then_snooze(test_client: TestClient):
    """Test that snoozing a dismissed notification works correctly"""
    today = date.today().isoformat()
    # Use a time that's due right now (within 5-minute window)
    from datetime import datetime, timedelta
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    payload = create_absolute_payload("DismissThenSnoozeDrug", current_time, today, today)
    r = test_client.post("/drug", json=payload)
    assert r.status_code == 200

    # fetch id
    list_resp = test_client.get("/drug").json()
    schedule = next(d for d in list_resp if d["name"] == "DismissThenSnoozeDrug")
    sid = schedule["id"]

    # Check notification appears initially
    notif_initial = test_client.get("/notifications").json()
    assert len(notif_initial) == 1

    # Dismiss first
    dismiss = test_client.post(f"/notifications/{sid}/dismiss")
    assert dismiss.status_code == 200

    # Verify dismiss worked
    notif1 = test_client.get("/notifications").json()
    assert len(notif1) == 0

    # Then snooze (should override the dismiss)
    snooze = test_client.post(f"/notifications/{sid}/snooze", json={"minutes": 20})
    assert snooze.status_code == 200

    # After snoozing, notification should still be gone (it's 20 minutes in the future)
    notif2 = test_client.get("/notifications").json()
    assert len(notif2) == 0


