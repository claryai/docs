#!/usr/bin/env python
"""
Container activation script for Clary AI.

This script activates a Clary AI container with an API key.
"""

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.api_key import ApiKey
from app.models.user import User


def generate_container_id():
    """
    Generate a unique container ID.

    Returns:
        str: A unique container ID.
    """
    # Try to get the machine ID
    machine_id = ""
    try:
        with open("/etc/machine-id", "r") as f:
            machine_id = f.read().strip()
    except Exception:
        pass

    # If we couldn't get the machine ID, use a random UUID
    if not machine_id:
        machine_id = str(uuid.uuid4())

    # Hash the machine ID to create a container ID
    return hashlib.sha256(machine_id.encode()).hexdigest()[:16]


def validate_api_key(api_key, container_id):
    """
    Validate an API key with the license server.

    Args:
        api_key: The API key to validate.
        container_id: The container ID.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    # Hash the API key for secure transmission
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    try:
        # Send validation request to license server
        response = requests.post(
            settings.LICENSE_SERVER_URL,
            json={
                "key_hash": key_hash,
                "container_id": container_id,
                "timestamp": int(time.time())
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("valid", False), data.get("tier", "free"), data.get("message", "")
        else:
            return False, "free", f"License server error: {response.status_code}"

    except Exception as e:
        return False, "free", f"License validation error: {str(e)}"


def save_license_cache(api_key, container_id, tier):
    """
    Save the license cache to disk.

    Args:
        api_key: The API key.
        container_id: The container ID.
        tier: The API key tier.
    """
    # Hash the API key for secure storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Create the cache directory if it doesn't exist
    cache_dir = os.path.join(settings.MODEL_PATH)
    os.makedirs(cache_dir, exist_ok=True)

    # Save the cache
    cache_file = os.path.join(cache_dir, ".license_cache")
    cache = {
        "valid_until": int(time.time()) + (settings.LICENSE_CHECK_INTERVAL * 3600),
        "container_id": container_id,
        "key_hash": key_hash,
        "tier": tier
    }

    try:
        with open(cache_file, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving license cache: {e}")


def create_admin_user(db_session, api_key, tier="standard"):
    """
    Create an admin user with the API key.

    Args:
        db_session: The database session.
        api_key: The API key.
        tier: The API key tier.

    Returns:
        User: The created user.
    """
    # Check if the admin user already exists
    user = db_session.query(User).filter(User.username == "admin").first()
    if not user:
        # Create the admin user
        user = User(
            username="admin",
            email="admin@claryai.local",
            password_hash=hashlib.sha256("admin".encode()).hexdigest(),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

    # Create the API key
    api_key_obj = db_session.query(ApiKey).filter(ApiKey.key == api_key).first()
    if not api_key_obj:
        api_key_obj = ApiKey(
            key=api_key,
            name="Container Activation Key",
            description="API key used to activate this container",
            user_id=user.id,
            tier=tier,  # Use the tier from the license validation
            is_active=True
        )
        db_session.add(api_key_obj)
        db_session.commit()

    return user


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Activate a Clary AI container with an API key")
    parser.add_argument("--api-key", required=True, help="The API key to use for activation")
    parser.add_argument("--container-id", help="The container ID (generated if not provided)")
    args = parser.parse_args()

    # Generate a container ID if not provided
    container_id = args.container_id or generate_container_id()

    print(f"Container ID: {container_id}")
    print("Validating API key...")

    # Validate the API key
    valid, tier, message = validate_api_key(args.api_key, container_id)
    if not valid:
        print(f"API key validation failed: {message}")
        sys.exit(1)

    print(f"API key is valid (tier: {tier})")

    # Save the license cache
    save_license_cache(args.api_key, container_id, tier)

    # Create the admin user with the API key
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        create_admin_user(db_session, args.api_key, tier)
        print("Admin user created with API key")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db_session.close()

    print("Container activation successful!")
    print(f"Container ID: {container_id}")
    print(f"API Key: {args.api_key}")
    print(f"Tier: {tier}")
    print(f"Valid until: {datetime.fromtimestamp(int(time.time()) + (settings.LICENSE_CHECK_INTERVAL * 3600))}")


if __name__ == "__main__":
    main()
