import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# USER_DATA_FILE = '../users.json'
# Get the directory of the current script (user_data.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the project root
project_root = os.path.dirname(current_dir)

# Define the path to users.json in the project root
USER_DATA_FILE = os.path.join(project_root, "users.json")


def load_users() -> Dict[str, Dict]:
    try:
        with open(USER_DATA_FILE, "r") as file:
            users = json.load(file)
        logger.info(f"Loaded {len(users)} users from {USER_DATA_FILE}")
        return users
    except FileNotFoundError:
        logger.warning(f"{USER_DATA_FILE} not found. Returning empty dict.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding {USER_DATA_FILE}. Returning empty dict.")
        return {}


def save_users(users: Dict[str, Dict]):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)


def get_user(identifier: str) -> Optional[Dict]:
    users = load_users()
    user = users.get(identifier)
    if not user:
        # If username lookup fails, try email lookup
        user = next(
            (data for data in users.values() if data["email"] == identifier), None
        )
    if user:
        logger.info(f"User found for identifier: {identifier}")
    else:
        logger.warning(f"User not found for identifier: {identifier}")
    return user


def add_user(username: str, email: str, hashed_password: str):
    users = load_users()
    users[username] = {"email": email, "password": hashed_password}
    save_users(users)
