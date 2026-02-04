"""
Tests for the Mergington High School API
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Basketball": {
            "description": "Team sport focused on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Volleyball": {
            "description": "Learn volleyball techniques and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["nina@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art techniques including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
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
        }
    }
    
    # Clear current activities and restore originals
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Basketball" in data
        assert "Volleyball" in data
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball"]
        assert "participants" in basketball
        assert "alex@mergington.edu" in basketball["participants"]
    
    def test_get_activities_includes_max_participants(self, client, reset_activities):
        """Test that activities include max_participants field"""
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball"]
        assert basketball["max_participants"] == 15


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity returns 404"""
        response = client.post(
            "/activities/NonexistentClub/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        # alex@mergington.edu is already signed up for Basketball
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students_to_same_activity(self, client, reset_activities):
        """Test that multiple different students can sign up for the same activity"""
        client.post("/activities/Basketball/signup?email=student1@mergington.edu")
        response = client.post(
            "/activities/Basketball/signup?email=student2@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify both are registered
        response = client.get("/activities")
        data = response.json()
        participants = data["Basketball"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete("/activities/Basketball/unregister?email=alex@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregister from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonexistentClub/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test that unregistering a non-registered student returns 400"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_can_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        # Unregister
        client.delete("/activities/Basketball/unregister?email=alex@mergington.edu")
        
        # Sign up again
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify they're registered
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" in data["Basketball"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
