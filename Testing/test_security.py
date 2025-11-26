from security import hash_password, verify_password, create_access_token, verify_token
from datetime import timedelta
from jose import jwt

class MockException(Exception):
    pass

def test_security():
    # Test Password Hashing
    password = "mysecretpassword"
    hashed = hash_password(password)
    print(f"Password hashed: {hashed}")
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
    print("Password verification successful")

    # Test Token Creation and Verification
    user_id = 123
    data = {"sub": str(user_id)}
    token = create_access_token(data)
    print(f"Token created: {token}")

    decoded_user_id = verify_token(token, MockException)
    print(f"Token verified, user_id: {decoded_user_id}")
    assert decoded_user_id == user_id
    
    # Test Expiration (Optional, hard to test without mocking time or short expiry)
    # Test Invalid Token
    try:
        verify_token("invalid.token.here", MockException)
    except MockException:
        print("Invalid token correctly raised exception")

if __name__ == "__main__":
    test_security()
