# Main entry point

from login import login_screen
from database import initialize_db

# Start of your script
if __name__ == "__main__":
    initialize_db()
    login_screen()

