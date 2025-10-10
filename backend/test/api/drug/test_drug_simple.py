import pytest
import os

# Set test database URL before importing backend modules
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test")

def test_add_drug(test_client):
    """Simple test to add a drug"""
    payload = {
        "name": "Aspirin",
        "kind": "pill",
        "amount_per_dose": 1,
        "duration": 5,
        "amount_per_day": 2,
    }
    
    resp = test_client.post("/drug", json=payload)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Added Aspirin"

def test_get_drugs(test_client):
    """Simple test to get all drugs"""
    resp = test_client.get("/drug")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

def test_add_duplicate_drug(test_client):
    """Test adding duplicate drug"""
    payload = {
        "name": "Aspirin",
        "kind": "pill",
        "amount_per_dose": 1,
        "duration": 5,
        "amount_per_day": 2,
    }
    
    # First add
    resp1 = test_client.post("/drug", json=payload)
    assert resp1.status_code == 200
    
    # Try to add again
    resp2 = test_client.post("/drug", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Drug already exists"

def test_update_drug(test_client):
    """Test updating a drug"""
    # First add a drug
    add_payload = {
        "name": "Ibuprofen",
        "kind": "pill",
        "amount_per_dose": 2,
        "duration": 7,
        "amount_per_day": 3,
    }
    resp = test_client.post("/drug", json=add_payload)
    assert resp.status_code == 200
    
    # Update the drug
    update_payload = {
        "name": "Ibuprofen",
        "kind": "pill",
        "amount_per_dose": 1,
        "duration": 5,
        "amount_per_day": 2,
    }
    resp = test_client.put("/drug/Ibuprofen", json=update_payload)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Updated Ibuprofen"

def test_delete_drug(test_client):
    """Test deleting a drug"""
    # First add a drug
    payload = {
        "name": "VitaminC",
        "kind": "pill",
        "amount_per_dose": 1,
        "duration": 10,
        "amount_per_day": 1,
    }
    resp = test_client.post("/drug", json=payload)
    assert resp.status_code == 200
    
    # Delete the drug
    resp = test_client.delete("/drug/VitaminC")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Deleted VitaminC"

def test_delete_nonexistent_drug(test_client):
    """Test deleting a drug that doesn't exist"""
    resp = test_client.delete("/drug/NonExistent")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Drug not found"
