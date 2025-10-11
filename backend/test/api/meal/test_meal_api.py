import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db
from backend.models import MealSchedule
from sqlalchemy.orm import Session

client = TestClient(app)

# Test data for all three meals
TEST_MEALS = [
    {"meal_name": "breakfast", "base_time": "08:00"},
    {"meal_name": "lunch", "base_time": "13:00"},
    {"meal_name": "dinner", "base_time": "19:00"}
]

def test_get_meal_schedules_empty():
    """Test getting meal schedules when none exist"""
    response = client.get("/meal-schedules")
    assert response.status_code == 200
    assert response.json() == []

def test_create_all_meals():
    """Test creating all three meal schedules (breakfast, lunch, dinner)"""
    for meal in TEST_MEALS:
        response = client.post("/meal-schedules", json=meal)
        assert response.status_code == 200
        assert f"Added {meal['meal_name']} meal schedule" in response.json()["message"]
    
    # Verify all meals were created
    response = client.get("/meal-schedules")
    assert response.status_code == 200
    meals = response.json()
    assert len(meals) == 3
    
    # Check that all meals exist and are in correct order
    meal_names = [meal["meal_name"] for meal in meals]
    assert meal_names == ["breakfast", "lunch", "dinner"]

def test_create_duplicate_meal_schedule():
    """Test creating a duplicate meal schedule fails"""
    # Create breakfast first
    client.post("/meal-schedules", json=TEST_MEALS[0])
    
    # Try to create duplicate breakfast
    response = client.post("/meal-schedules", json=TEST_MEALS[0])
    assert response.status_code == 400
    assert "Meal schedule already exists" in response.json()["detail"]

def test_get_all_meal_schedules():
    """Test getting all meal schedules after creating them"""
    # Create all meals
    for meal in TEST_MEALS:
        client.post("/meal-schedules", json=meal)
    
    response = client.get("/meal-schedules")
    assert response.status_code == 200
    meals = response.json()
    assert len(meals) == 3
    
    # Verify each meal has correct data
    for i, expected_meal in enumerate(TEST_MEALS):
        actual_meal = meals[i]
        assert actual_meal["meal_name"] == expected_meal["meal_name"]
        assert actual_meal["base_time"] == expected_meal["base_time"]
        assert "id" in actual_meal
        assert "created_at" in actual_meal

def test_update_breakfast_time():
    """Test updating breakfast time specifically"""
    # Create all meals
    for meal in TEST_MEALS:
        client.post("/meal-schedules", json=meal)
    
    # Update only breakfast time
    update_data = {
        "base_time": "07:30"
    }
    response = client.put("/meal-schedules/breakfast", json=update_data)
    assert response.status_code == 200
    assert "Updated breakfast meal schedule" in response.json()["message"]
    
    # Verify only breakfast was updated
    response = client.get("/meal-schedules")
    meals = response.json()
    
    breakfast = next(meal for meal in meals if meal["meal_name"] == "breakfast")
    lunch = next(meal for meal in meals if meal["meal_name"] == "lunch")
    dinner = next(meal for meal in meals if meal["meal_name"] == "dinner")
    
    assert breakfast["base_time"] == "07:30"  # Updated
    assert lunch["base_time"] == "13:00"     # Unchanged
    assert dinner["base_time"] == "19:00"    # Unchanged

def test_update_lunch_time():
    """Test updating lunch time while keeping others unchanged"""
    # Create all meals
    for meal in TEST_MEALS:
        client.post("/meal-schedules", json=meal)
    
    # Update only lunch time
    update_data = {
        "base_time": "12:30"  # Change lunch time
    }
    response = client.put("/meal-schedules/lunch", json=update_data)
    assert response.status_code == 200
    assert "Updated lunch meal schedule" in response.json()["message"]
    
    # Verify only lunch was updated
    response = client.get("/meal-schedules")
    meals = response.json()
    
    breakfast = next(meal for meal in meals if meal["meal_name"] == "breakfast")
    lunch = next(meal for meal in meals if meal["meal_name"] == "lunch")
    dinner = next(meal for meal in meals if meal["meal_name"] == "dinner")
    
    assert breakfast["base_time"] == "08:00"  # Unchanged
    assert lunch["base_time"] == "12:30"     # Updated
    assert dinner["base_time"] == "19:00"    # Unchanged

def test_update_dinner_time():
    """Test updating dinner time"""
    # Create all meals
    for meal in TEST_MEALS:
        client.post("/meal-schedules", json=meal)
    
    # Update dinner time
    update_data = {
        "base_time": "20:30"
    }
    response = client.put("/meal-schedules/dinner", json=update_data)
    assert response.status_code == 200
    assert "Updated dinner meal schedule" in response.json()["message"]
    
    # Verify dinner was updated correctly
    response = client.get("/meal-schedules")
    meals = response.json()
    
    dinner = next(meal for meal in meals if meal["meal_name"] == "dinner")
    assert dinner["base_time"] == "20:30"

def test_update_nonexistent_meal_schedule():
    """Test updating a non-existent meal schedule fails"""
    update_data = {
        "base_time": "20:00"
    }
    response = client.put("/meal-schedules/nonexistent", json=update_data)
    assert response.status_code == 404
    assert "Meal schedule not found" in response.json()["detail"]

def test_delete_breakfast_keep_others():
    """Test deleting breakfast while keeping lunch and dinner"""
    # Create all meals
    for meal in TEST_MEALS:
        client.post("/meal-schedules", json=meal)
    
    # Delete only breakfast
    response = client.delete("/meal-schedules/breakfast")
    assert response.status_code == 200
    assert "Deleted breakfast meal schedule" in response.json()["message"]
    
    # Verify only breakfast was deleted
    response = client.get("/meal-schedules")
    meals = response.json()
    assert len(meals) == 2
    
    meal_names = [meal["meal_name"] for meal in meals]
    assert "breakfast" not in meal_names
    assert "lunch" in meal_names
    assert "dinner" in meal_names

def test_delete_nonexistent_meal_schedule():
    """Test deleting a non-existent meal schedule fails"""
    response = client.delete("/meal-schedules/nonexistent")
    assert response.status_code == 404
    assert "Meal schedule not found" in response.json()["detail"]

def test_invalid_time_format():
    """Test that invalid time format is rejected"""
    meal_data = {
        "meal_name": "breakfast",
        "base_time": "25:00"  # Invalid time
    }
    response = client.post("/meal-schedules", json=meal_data)
    assert response.status_code == 400
    assert "Invalid time format" in response.json()["detail"]

def test_realistic_meal_management_workflow():
    """Test a realistic workflow: create all meals, update some, delete one"""
    # Step 1: Create all three meals
    for meal in TEST_MEALS:
        response = client.post("/meal-schedules", json=meal)
        assert response.status_code == 200
    
    # Step 2: Verify all meals exist
    response = client.get("/meal-schedules")
    meals = response.json()
    assert len(meals) == 3
    
    # Step 3: Update breakfast to earlier time
    response = client.put("/meal-schedules/breakfast", json={
        "base_time": "07:00"
    })
    assert response.status_code == 200
    
    # Step 4: Update lunch to different time
    response = client.put("/meal-schedules/lunch", json={
        "base_time": "12:30"
    })
    assert response.status_code == 200
    
    # Step 5: Update dinner to later time
    response = client.put("/meal-schedules/dinner", json={
        "base_time": "20:00"
    })
    assert response.status_code == 200
    
    # Step 6: Verify all changes
    response = client.get("/meal-schedules")
    meals = response.json()
    
    breakfast = next(meal for meal in meals if meal["meal_name"] == "breakfast")
    lunch = next(meal for meal in meals if meal["meal_name"] == "lunch")
    dinner = next(meal for meal in meals if meal["meal_name"] == "dinner")
    
    assert breakfast["base_time"] == "07:00"
    assert lunch["base_time"] == "12:30"
    assert dinner["base_time"] == "20:00"
    
    # Step 7: Delete lunch
    response = client.delete("/meal-schedules/lunch")
    assert response.status_code == 200
    
    # Step 8: Verify final state
    response = client.get("/meal-schedules")
    meals = response.json()
    assert len(meals) == 2
    
    meal_names = [meal["meal_name"] for meal in meals]
    assert "breakfast" in meal_names
    assert "lunch" not in meal_names
    assert "dinner" in meal_names
