import pytest
from fastapi.testclient import TestClient
from test_auth import Test_user_1, Test_user_2

# --- Helper to get token for any test user ---
def get_auth_headers(client: TestClient, user_data: dict):
    # Register
    client.post("/auth/register", json=user_data)
    # Login
    response = client.post("/auth/token", data={
        "username": user_data["email"], 
        "password": user_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- 1. TEST: CREATE AND READ ---
def test_create_and_read_todo(client: TestClient):
    headers = get_auth_headers(client, Test_user_1)
    
    # Create
    todo_payload = {"title": "Learn FastAPI", "priority": 5, "description": "Finish the router"}
    create_res = client.post("/todos/", json=todo_payload, headers=headers)
    
    # FIX: Assert success before accessing the ID to avoid KeyError
    assert create_res.status_code == 201, f"Create failed: {create_res.json()}"
    
    # Read All
    read_res = client.get("/todos/", headers=headers)
    assert read_res.status_code == 200
    assert len(read_res.json()) == 1
    assert read_res.json()[0]["title"] == "Learn FastAPI"


# --- 2. TEST: UPDATE (Partial) ---
def test_update_todo_status(client: TestClient):
    headers = get_auth_headers(client, Test_user_1)
    
    # Create
    create_res = client.post("/todos/", json={"title": "Test Task", "priority": 1}, headers=headers)
    todo_id = create_res.json()["id"]
    
    # Update only 'complete' status
    update_res = client.put(f"/todos/{todo_id}", json={"complete": True}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["complete"] is True
    # Ensure title didn't disappear
    assert update_res.json()["title"] == "Test Task"

# --- 3. TEST: PRIVACY ISOLATION (Crucial) ---
def test_user_isolation(client: TestClient):
    # User 1 (e.g., ID 142010) creates a private task
    headers1 = get_auth_headers(client, Test_user_1)
    create_res = client.post("/todos/", json={"title": "User 1 Secret", "priority": 1}, headers=headers1)
    todo_id = create_res.json()["id"]
    
    # User 2 logs in
    headers2 = get_auth_headers(client, Test_user_2)
    
    # User 2 tries to GET User 1's task
    get_res = client.get(f"/todos/{todo_id}", headers=headers2)
    assert get_res.status_code == 404 # Your utility raises 404 for unauthorized
    
    # User 2 tries to DELETE User 1's task
    del_res = client.delete(f"/todos/{todo_id}", headers=headers2)
    assert del_res.status_code == 404

# --- 4. TEST: DELETE ---
def test_delete_own_todo(client: TestClient):
    headers = get_auth_headers(client, Test_user_1)
    
    # Create
    create_res = client.post("/todos/", json={"title": "Delete Me", "priority": 1}, headers=headers)
    todo_id = create_res.json()["id"]
    
    # Delete
    response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's gone
    verify_res = client.get(f"/todos/{todo_id}", headers=headers)
    assert verify_res.status_code == 404

# --- 5. TEST: INVALID PATH ---
def test_invalid_todo_id(client: TestClient):
    headers = get_auth_headers(client, Test_user_1)
    # Testing Path(gt=0)
    response = client.get("/todos/0", headers=headers)
    assert response.status_code == 422 # Validation error