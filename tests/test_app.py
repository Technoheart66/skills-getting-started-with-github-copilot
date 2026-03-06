"""
Tests for the Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_success(self, client, reset_activities):
        """
        Arrange: No setup needed
        Act: Send GET request to /activities
        Assert: Response should contain all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
    def test_activities_have_correct_structure(self, client, reset_activities):
        """
        Arrange: No setup needed
        Act: Send GET request to /activities
        Assert: Each activity should have required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            
    def test_root_redirects_to_static(self, client, reset_activities):
        """
        Arrange: No setup needed
        Act: Send GET request to /
        Assert: Should redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """
        Arrange: Student wants to sign up for an activity with available spots
        Act: Send POST request to signup endpoint
        Assert: Student should be added and receive success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify student was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        
    def test_signup_duplicate_student_fails(self, client, reset_activities):
        """
        Arrange: A student is already registered for an activity
        Act: Try to sign up the same student again
        Assert: Should fail with 400 status and appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        
    def test_signup_activity_full_fails(self, client, reset_activities):
        """
        Arrange: An activity is at max capacity
        Act: Try to sign up a new student for the full activity
        Assert: Should fail with 400 status and "full" error message
        """
        # Arrange
        activity_name = "Debate Team"  # max_participants = 12, has 2 participants
        # Fill up the activity
        for i in range(10):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Act: Try to add one more student when activity is full
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "finalstudent@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]
        
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Student wants to sign up for an activity that doesn't exist
        Act: Send POST request with invalid activity name
        Assert: Should fail with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """
        Arrange: A student is registered for an activity
        Act: Send POST request to unregister the student
        Assert: Student should be removed successfully
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify student is currently registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify student was actually removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
        
    def test_unregister_not_registered_fails(self, client, reset_activities):
        """
        Arrange: A student is NOT registered for an activity
        Act: Try to unregister the student
        Assert: Should fail with 400 status and appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
        
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Try to unregister from an activity that doesn't exist
        Act: Send POST request with invalid activity name
        Assert: Should fail with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
        
    def test_unregister_opens_spot_for_new_signup(self, client, reset_activities):
        """
        Arrange: Activity is full and a student unregisters
        Act: First unregister a student, then try to sign up a new one
        Assert: New student should be able to sign up after spot is freed
        """
        # Arrange
        activity_name = "Debate Team"  # max_participants = 12
        # Fill up the activity
        for i in range(10):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Verify activity is full
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "shouldfail@mergington.edu"}
        )
        assert response.status_code == 400
        
        # Act: Unregister a student
        original_participant = "grace@mergington.edu"
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": original_participant}
        )
        
        # Try to sign up new student
        new_email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify new student is registered
        activities_response = client.get("/activities")
        assert new_email in activities_response.json()[activity_name]["participants"]
