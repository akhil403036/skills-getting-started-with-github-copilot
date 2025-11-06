import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Check if activities have the required fields
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_activity():
    # Test successful signup
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Test signing up same person twice
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_invalid_activity():
    response = client.post("/activities/NonexistentClub/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()



def test_max_participants():
    activity_name = "Chess Club"
    # Get current participants count
    activities = client.get("/activities").json()
    current_count = len(activities[activity_name]["participants"])
    max_participants = activities[activity_name]["max_participants"]
    
    # Fill up remaining spots
    for i in range(current_count, max_participants):
        email = f"runner{i}@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 200
    
    # Try to add one more participant
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "extra@mergington.edu"})
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()