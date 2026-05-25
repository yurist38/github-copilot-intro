"""Backend API tests for the FastAPI application."""

from src.app import activities


def test_get_activities_returns_seeded_data(client):
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Music Band",
        "Debate Club",
        "Robotics Team",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity_names.issubset(payload.keys())
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant_to_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    starting_participants = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == starting_participants + 1


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    starting_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities[activity_name]["participants"] == starting_participants


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    activity_name = "Gym Class"
    email = "remove.me@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    starting_participants = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == starting_participants - 1


def test_unregister_rejects_missing_participant(client):
    # Arrange
    activity_name = "Art Studio"
    email = "missing.student@mergington.edu"
    starting_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activities[activity_name]["participants"] == starting_participants


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Astronomy Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Astronomy Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
