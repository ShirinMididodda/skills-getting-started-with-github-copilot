def test_initial_data_integrity(client):
    """Test that initial activity data is correct"""
    response = client.get("/activities")
    activities = response.json()

    # Check Chess Club has initial participants
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]

    # Check max_participants
    assert chess_club["max_participants"] == 12


def test_signup_multiple_activities(client):
    """Test that a student can sign up for multiple activities"""
    email = "multi@example.com"

    # Sign up for two different activities
    client.post("/activities/Art Studio/signup?email=multi@example.com")
    client.post("/activities/Drama Workshop/signup?email=multi@example.com")

    # Verify in both
    response = client.get("/activities")
    activities = response.json()
    assert email in activities["Art Studio"]["participants"]
    assert email in activities["Drama Workshop"]["participants"]


def test_signup_empty_email(client):
    """Test signup with empty email (edge case)"""
    response = client.post("/activities/Chess Club/signup?email=")
    assert response.status_code == 200  # App doesn't validate email format
    data = response.json()
    assert "Signed up  for Chess Club" in data["message"]

    # Verify empty email was added
    response = client.get("/activities")
    activities = response.json()
    assert "" in activities["Chess Club"]["participants"]


def test_signup_special_characters_email(client):
    """Test signup with special characters in email"""
    email = "test+special@example.com"
    response = client.post("/activities/Science Olympiad/signup?email=test+special@example.com")
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for Science Olympiad" in data["message"]

    # Verify
    response = client.get("/activities")
    activities = response.json()
    assert email in activities["Science Olympiad"]["participants"]


def test_capacity_not_enforced(client):
    """Test that capacity limits are not currently enforced (business logic gap)"""
    # Sign up more than max_participants for Chess Club (max 12, currently 2)
    for i in range(15):
        email = f"extra{i}@example.com"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200

    # Check that all were added (even though over capacity)
    response = client.get("/activities")
    activities = response.json()
    chess_participants = activities["Chess Club"]["participants"]
    assert len(chess_participants) > 12  # More than max allowed