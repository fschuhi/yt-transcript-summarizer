import json
from typing import Dict, Optional

USER_DATA_FILE = 'users.json'


def load_users() -> Dict[str, Dict]:
    try:
        with open(USER_DATA_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users


def save_users(users: Dict[str, Dict]):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)


def get_user(username: str) -> Optional[Dict]:
    users = load_users()
    return users.get(username)


def add_user(username: str, email: str, hashed_password: str):
    users = load_users()
    users[username] = {
        'email': email,
        'password': hashed_password
    }
    save_users(users)