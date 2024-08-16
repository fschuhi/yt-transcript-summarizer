import json
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

USER_DATA_FILE = '../users.json'


def load_users() -> Dict[str, Dict]:
    try:
        with open(USER_DATA_FILE, 'r') as file:
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
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)


def get_user(username: str) -> Optional[Dict]:
    users = load_users()
    user = users.get(username)
    if user:
        logger.info(f"User {username} found")
    else:
        logger.warning(f"User {username} not found")
    return user


def add_user(username: str, email: str, hashed_password: str):
    users = load_users()
    users[username] = {
        'email': email,
        'password': hashed_password
    }
    save_users(users)