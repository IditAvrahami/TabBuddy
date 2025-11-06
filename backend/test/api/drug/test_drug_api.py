import pytest
import os

# Set test database URL before importing backend modules
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test")

from backend.test.conftest import get_db_count, get_db_drug


def test_add_drug_success(db_session, test_client):
    payload = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    
    # Check initial DB state
    initial_count = get_db_count(db_session)
    
    resp = test_client.post("/drug", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == payload['name']
    assert data["kind"] == payload['kind']
    assert data["amount_per_dose"] == payload['amount_per_dose']
    assert data["duration"] == payload['duration']
    assert data["amount_per_day"] == payload['amount_per_day']
    
    # Verify drug was added to database (integration check)
    assert get_db_count(db_session) == initial_count + 1


def test_add_drug_duplicate(db_session, test_client):
    payload = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    
    # First, add the drug
    resp1 = test_client.post("/drug", json=payload)
    assert resp1.status_code == 200
    
    # Check DB state before duplicate attempt
    count_before = get_db_count(db_session)
    
    # Try to add the same drug again
    resp = test_client.post("/drug", json=payload)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Drug already exists"
    
    # Verify no new drug was added to database
    assert get_db_count(db_session) == count_before


def test_get_all_drugs(db_session, test_client):
    # Add a drug first
    payload = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    create_resp = test_client.post("/drug", json=payload)
    assert create_resp.status_code == 200
    created_drug = create_resp.json()
    
    # Check DB state before API call
    db_count = get_db_count(db_session)
    
    resp = test_client.get("/drug")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == db_count
    assert any(d["name"] == "Paracetamol" for d in data)
    
    # Verify API response matches the created drug
    api_drug = next(d for d in data if d["name"] == "Paracetamol")
    assert api_drug["kind"] == created_drug["kind"]
    assert api_drug["amount_per_dose"] == created_drug["amount_per_dose"]
    assert api_drug["duration"] == created_drug["duration"]
    assert api_drug["amount_per_day"] == created_drug["amount_per_day"]


def test_update_drug_success(db_session, test_client):
    # First, add a drug to update
    initial_payload = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    create_resp = test_client.post("/drug", json=initial_payload)
    assert create_resp.status_code == 200
    created_drug = create_resp.json()
    assert created_drug["amount_per_dose"] == 2  # Original value
    
    updated = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 1,
        "duration": 5,
        "amount_per_day": 2,
    }
    
    # Check DB state before update
    count_before = get_db_count(db_session)
    
    resp = test_client.put(f"/drug/{updated['name']}", json=updated)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == updated['name']
    assert data["amount_per_dose"] == updated['amount_per_dose']
    assert data["duration"] == updated['duration']
    assert data["amount_per_day"] == updated['amount_per_day']
    
    # Verify drug count unchanged but data updated
    assert get_db_count(db_session) == count_before


def test_update_drug_not_found(db_session, test_client):
    missing = {
        "name": "NonExistent",
        "kind": "liquid",
        "amount_per_dose": 10,
        "duration": 3,
        "amount_per_day": 1,
    }
    
    # Check DB state before failed update
    count_before = get_db_count(db_session)
    
    resp = test_client.put(f"/drug/{missing['name']}", json=missing)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Drug not found"
    
    # Verify no changes to database
    assert get_db_count(db_session) == count_before
    assert get_db_drug(db_session, "NonExistent") is None


def test_delete_drug_success(db_session, test_client):
    # First, add a drug to delete
    payload = {
        "name": "Paracetamol",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    create_resp = test_client.post("/drug", json=payload)
    assert create_resp.status_code == 200
    created_drug = create_resp.json()
    assert created_drug["name"] == "Paracetamol"
    
    # Check DB state before deletion
    count_before = get_db_count(db_session)
    
    resp = test_client.delete("/drug/Paracetamol")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Paracetamol"
    
    # Verify drug was removed from database
    assert get_db_count(db_session) == count_before - 1


def test_delete_drug_not_found(db_session, test_client):
    # Check DB state before failed deletion
    count_before = get_db_count(db_session)
    assert get_db_drug(db_session, "Paracetamol") is None  # Already deleted in previous test
    
    resp = test_client.delete("/drug/Paracetamol")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Drug not found"
    
    # Verify no changes to database
    assert get_db_count(db_session) == count_before
