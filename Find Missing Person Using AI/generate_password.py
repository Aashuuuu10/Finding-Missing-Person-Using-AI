"""
Script to generate bcrypt-hashed passwords for login_config.yml
"""

import bcrypt


def generate_bcrypt_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


if __name__ == "__main__":
    password = input("Enter the password to hash: ")
    hashed_password = generate_bcrypt_password(password)
    print(f"\nBcrypt hashed password:\n{hashed_password}")
    print(f"\nPaste this into login_config.yml as:")
    print(f"      password: '{hashed_password}'")
