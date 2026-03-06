import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state before each test"""
    initial_state = {
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
            "description": "Competitive basketball team for intramural tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Band, orchestra, and vocal performance groups",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 30,
            "participants": ["hannah@mergington.edu", "lucas@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build competitive robots",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["grace@mergington.edu", "ryan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(copy.deepcopy(initial_state))
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(initial_state))
