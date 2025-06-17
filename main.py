from database import initialize_db, seed_initial_data

# Initialize DB before anything else
initialize_db()
seed_initial_data()

from login import login_screen

# Start of your script
if __name__ == "__main__":
    login_screen()
