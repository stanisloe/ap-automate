import hashlib

def password_to_key(password: str) -> bytes:
    salt = hashlib.sha256(password.encode()).digest()[:16]
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations=100000, dklen=32)
    return key

# Example usage
password = "opevmye0u09tcwau09g09ym0cawm0"    # Regular password
key = password_to_key(password)
print(key.hex())