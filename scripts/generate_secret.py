#!/usr/bin/env python
import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print(f"SECRET_KEY={generate_secret_key()}")
