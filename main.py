"""Online Quiz System - command-line, menu-driven application.

This is the entry point. Users log in or register first; then admins get a
question-management menu and normal users get a quiz menu. Quiz data, users,
and scores are stored in a SQLite database.

Run with:  python main.py
"""

import getpass
import sqlite3
import sys

import auth
import database
import quiz

LEVELS = database.LEVELS

# Default admin account seeded on first run (change the password afterwards).
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


# --------------------------------------------------------------------------- #
# Input helpers
# --------------------------------------------------------------------------- #
def prompt_nonempty(message):
    """Ask for text and keep asking until the user types something."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("    This field cannot be empty. Please try again.")


def prompt_menu_choice(message, valid_choices):
    """Ask for a menu number and return it only if it is in valid_choices."""
    valid = {str(c) for c in valid_choices}
    while True:
        choice = input(message).strip()
        if choice in valid:
            return choice
        print(f"    Please enter one of: {', '.join(sorted(valid))}.")


def prompt_password(message):
    """Read a password without echoing it to the terminal."""
    return getpass.getpass(message)


def prompt_level():
    """Ask the user to pick a difficulty level and return it as text."""
    print("\nSelect a level:")
    print("  1. Easy   2. Medium   3. Hard")
    choice = prompt_menu_choice(">>> Enter your choice (1-3): ", [1, 2, 3])
    return {"1": "easy", "2": "medium", "3": "hard"}[choice]


# --------------------------------------------------------------------------- #
# Authentication screen
# --------------------------------------------------------------------------- #
def register_flow():
    """Register a new user account. Returns the user dict or None on cancel."""
    print("\n--- Register ---")
    username = prompt_nonempty(">>> Choose a username: ")
    password = prompt_password(">>> Choose a password: ")
    confirm = prompt_password(">>> Confirm password: ")
    if password != confirm:
        print("    Passwords do not match. Please try again.")
        return None

    user, error = auth.register(username, password)
    if error:
        print(f"    {error}")
        return None

    print(f"\nWelcome, {user['username']}! Your account has been created.")
    return user


def login_flow():
    """Log an existing user in. Returns the user dict or None on failure."""
    print("\n--- Login ---")
    username = prompt_nonempty(">>> Username: ")
    password = prompt_password(">>> Password: ")

    user = auth.login(username, password)
    if user is None:
        print("    Invalid username or password.")
        return None

    print(f"\nLogged in as {user['username']} ({user['role']}).")
    return user


def auth_screen():
    """Show the login/register screen. Returns a user dict, or None to exit."""
    while True:
        print("\n===== ONLINE QUIZ SYSTEM =====")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = prompt_menu_choice(">>> Enter your choice (1-3): ", [1, 2, 3])

        if choice == "1":
            user = login_flow()
        elif choice == "2":
            user = register_flow()
        else:  # "3"
            return None

        if user is not None:
            return user


# --------------------------------------------------------------------------- #
# User menu actions
# --------------------------------------------------------------------------- #
def take_quiz(user):
    """Let the logged-in user take a quiz."""
    level = prompt_level()
    quiz.run_quiz(user, level)


def view_my_history(user):
    """Show the logged-in user's own past attempts."""
    print("\n--- My Quiz History ---")
    rows = database.get_scores_by_user(user["id"], limit=20)
    if not rows:
        print("You have not taken any quizzes yet.")
        return

    print(f"{'Level':<10}{'Score':<10}{'Date'}")
    print("-" * 40)
    for row in rows:
        score_text = f"{row['score']}/{row['total']}"
        taken = str(row["taken_at"])[:16]
        print(f"{row['level']:<10}{score_text:<10}{taken}")


def show_leaderboard():
    """Display top quiz players by average score."""
    print("\n--- Leaderboard ---")
    rows = database.get_score_history(limit=100)
    if not rows:
        print("No scores available.")
        return

    ranking = {}
    for row in rows:
        name = row["player_name"]
        percentage = (row["score"] / row["total"]) * 100
        ranking.setdefault(name, []).append(percentage)

    results = [(name, sum(scores) / len(scores)) for name, scores in ranking.items()]
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Player':<20}{'Average Score'}")
    print("-" * 40)
    for player, score in results[:10]:
        print(f"{player:<20}{score:.2f}%")


# --------------------------------------------------------------------------- #
# Admin menu actions
# --------------------------------------------------------------------------- #
def add_question():
    """Create: add a new question to the database."""
    print("\n--- Add a New Question ---")
    level = prompt_level()
    text = prompt_nonempty(">>> Question text: ")
    opt_a = prompt_nonempty(">>> Option A: ")
    opt_b = prompt_nonempty(">>> Option B: ")
    opt_c = prompt_nonempty(">>> Option C: ")
    opt_d = prompt_nonempty(">>> Option D: ")
    correct = prompt_menu_choice(
        ">>> Which option is correct? (A/B/C/D): ", ["A", "B", "C", "D"]
    )
    new_id = database.add_question(level, text, opt_a, opt_b, opt_c, opt_d, correct)
    print(f"\nQuestion added successfully (id #{new_id}).")


def view_all_questions():
    """Read: list every question in the database."""
    print("\n--- All Questions ---")
    rows = database.get_all_questions()
    if not rows:
        print("There are no questions yet.")
        return

    print(f"{'ID':<5}{'Level':<10}{'Correct':<9}{'Question'}")
    print("-" * 70)
    for row in rows:
        text = row["question_text"]
        if len(text) > 45:
            text = text[:42] + "..."
        print(f"{row['id']:<5}{row['level']:<10}{row['correct_option']:<9}{text}")


def update_question():
    """Update: edit an existing question by id."""
    print("\n--- Update a Question ---")
    view_all_questions()
    qid = prompt_nonempty("\n>>> Enter the ID of the question to update: ")
    if not qid.isdigit():
        print("    That is not a valid ID.")
        return

    existing = database.get_question_by_id(int(qid))
    if existing is None:
        print(f"    No question found with ID {qid}.")
        return

    print(f"\nEditing question #{qid}. Enter the new values.")
    print(f"(Current question: {existing['question_text']})")
    level = prompt_level()
    text = prompt_nonempty(">>> Question text: ")
    opt_a = prompt_nonempty(">>> Option A: ")
    opt_b = prompt_nonempty(">>> Option B: ")
    opt_c = prompt_nonempty(">>> Option C: ")
    opt_d = prompt_nonempty(">>> Option D: ")
    correct = prompt_menu_choice(
        ">>> Which option is correct? (A/B/C/D): ", ["A", "B", "C", "D"]
    )

    changed = database.update_question(
        int(qid), level, text, opt_a, opt_b, opt_c, opt_d, correct
    )
    if changed:
        print(f"\nQuestion #{qid} updated successfully.")
    else:
        print(f"\nNothing was updated for question #{qid}.")


def delete_question():
    """Delete: remove a question by id, with confirmation."""
    print("\n--- Delete a Question ---")
    view_all_questions()
    qid = prompt_nonempty("\n>>> Enter the ID of the question to delete: ")
    if not qid.isdigit():
        print("    That is not a valid ID.")
        return

    existing = database.get_question_by_id(int(qid))
    if existing is None:
        print(f"    No question found with ID {qid}.")
        return

    print(f"\nYou are about to delete: {existing['question_text']}")
    confirm = prompt_menu_choice(">>> Are you sure? (Y/N): ", ["Y", "N", "y", "n"])
    if confirm.upper() == "Y":
        deleted = database.delete_question(int(qid))
        if deleted:
            print(f"Question #{qid} deleted.")
    else:
        print("Delete cancelled.")


def view_all_scores():
    """Show recent quiz attempts across all users."""
    print("\n--- All Scores ---")
    rows = database.get_score_history(limit=20)
    if not rows:
        print("No quizzes have been taken yet.")
        return

    print(f"{'Name':<20}{'Level':<10}{'Score':<10}{'Date'}")
    print("-" * 60)
    for row in rows:
        score_text = f"{row['score']}/{row['total']}"
        taken = str(row["taken_at"])[:16]
        print(f"{row['player_name']:<20}{row['level']:<10}{score_text:<10}{taken}")


def show_about():
    """Print information about the system."""
    print("""
--- About Online Quiz System ---

Features:
- User accounts with admin and user roles
- Multiple difficulty levels
- SQLite database storage
- Score tracking and leaderboard
- Admin question management (add, view, update, delete)

Developed as a command-line quiz application.
""")


# --------------------------------------------------------------------------- #
# Menus (per role)
# --------------------------------------------------------------------------- #
def admin_menu(user):
    """Menu shown to admin users; returns on logout."""
    while True:
        print(f"\n===== ADMIN MENU (logged in as {user['username']}) =====")
        print("1. Add a Question")
        print("2. View All Questions")
        print("3. Update a Question")
        print("4. Delete a Question")
        print("5. View All Scores")
        print("6. About")
        print("7. Logout")
        choice = prompt_menu_choice(
            ">>> Enter your choice (1-7): ", [1, 2, 3, 4, 5, 6, 7]
        )

        try:
            if choice == "1":
                add_question()
            elif choice == "2":
                view_all_questions()
            elif choice == "3":
                update_question()
            elif choice == "4":
                delete_question()
            elif choice == "5":
                view_all_scores()
            elif choice == "6":
                show_about()
            elif choice == "7":
                print(f"\nLogged out. Goodbye, {user['username']}!")
                return
        except sqlite3.Error as exc:
            print(f"\n[Database error] {exc}")
            print("Returning to the menu.")


def user_menu(user):
    """Menu shown to normal users; returns on logout."""
    while True:
        print(f"\n===== USER MENU (logged in as {user['username']}) =====")
        print("1. Take a Quiz")
        print("2. View My History")
        print("3. Leaderboard")
        print("4. About")
        print("5. Logout")
        choice = prompt_menu_choice(">>> Enter your choice (1-5): ", [1, 2, 3, 4, 5])

        try:
            if choice == "1":
                take_quiz(user)
            elif choice == "2":
                view_my_history(user)
            elif choice == "3":
                show_leaderboard()
            elif choice == "4":
                show_about()
            elif choice == "5":
                print(f"\nLogged out. Goodbye, {user['username']}!")
                return
        except sqlite3.Error as exc:
            print(f"\n[Database error] {exc}")
            print("Returning to the menu.")


def main():
    """Set up the database, then run the auth screen and role-based menus."""
    print("Welcome to the Online Quiz System!")
    print("Initialising the database...")

    if not database.init_database():
        print("\nCould not set up the database. Please check DB_PATH in .env.")
        sys.exit(1)

    database.seed_questions_if_empty()
    database.seed_admin_if_missing(
        DEFAULT_ADMIN_USERNAME, auth.hash_password(DEFAULT_ADMIN_PASSWORD)
    )
    print("Ready!")

    while True:
        user = auth_screen()
        if user is None:
            print("\nThank you for using the Online Quiz System. Goodbye!")
            break

        if user["role"] == "admin":
            admin_menu(user)
        else:
            user_menu(user)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
