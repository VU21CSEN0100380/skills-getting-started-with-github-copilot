"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the competitive basketball team for games and tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Play soccer and develop athletic skills",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["ryan@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and various art techniques",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu"]
        },
        "Music Band": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["jacob@mergington.edu", "chloe@mergington.edu"]
        }
    }
    
    # Clear and restore
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for getting all activities"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for signing up for activities"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        chess_activity = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess_activity["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_enrolled(self, client):
        """Test signup for an activity when already enrolled"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}  # Already in Chess Club
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can signup for multiple activities"""
        student_email = "newstudent@mergington.edu"
        
        # Signup for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": student_email}
        )
        assert response1.status_code == 200
        
        # Signup for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": student_email}
        )
        assert response2.status_code == 200
        
        # Verify both signups were successful
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert student_email in data["Chess Club"]["participants"]
        assert student_email in data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for unregistering from activities"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" not in data["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_enrolled(self, client):
        """Test unregister from an activity when not enrolled"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_signup_then_unregister(self, client):
        """Test signup and then unregister"""
        student_email = "newstudent@mergington.edu"
        
        # Signup
        response1 = client.post(
            "/activities/Art Studio/signup",
            params={"email": student_email}
        )
        assert response1.status_code == 200
        
        # Verify signup
        activities_response1 = client.get("/activities")
        assert student_email in activities_response1.json()["Art Studio"]["participants"]
        
        # Unregister
        response2 = client.post(
            "/activities/Art Studio/unregister",
            params={"email": student_email}
        )
        assert response2.status_code == 200
        
        # Verify unregister
        activities_response2 = client.get("/activities")
        assert student_email not in activities_response2.json()["Art Studio"]["participants"]


class TestActivityCapacity:
    """Tests related to activity capacity constraints"""
    
    def test_activities_have_capacity_limits(self, client):
        """Test that activities have max_participants set"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
