from schemas import UserCreate, TodoCreate, UserOut, TodoOut

def test_schemas():
    # Test User Schema
    user_data = {
        "email": "test@example.com",
        "phone_number": "1234567890",
        "role": "user",
        "password": "password123"
    }
    user_create = UserCreate(**user_data)
    print(f"UserCreate valid: {user_create}")

    user_response_data = {
        "email": "test@example.com",
        "phone_number": "1234567890",
        "role": "user",
        "unique_id": 1
    }
    user = User(**user_response_data)
    print(f"User valid: {user}")

    # Test Todo Schema
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": 1,
        "complete": False
    }
    todo_create = TodoCreate(**todo_data)
    print(f"TodoCreate valid: {todo_create}")

    todo_response_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": 1,
        "complete": False,
        "unique_id": 1,
        "owner_id": 1
    }
    todo = Todo(**todo_response_data)
    print(f"Todo valid: {todo}")

if __name__ == "__main__":
    test_schemas()
