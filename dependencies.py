# dependencies.py

import sys
import subprocess


def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def ensure_dependencies():
    try:
        install_requirements()
        print("All dependencies are installed.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please check your internet connection and try again.")


if __name__ == "__main__":
    ensure_dependencies()
