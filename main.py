"""Online Quiz System - command-line, menu-driven application.

This is the entry point. It shows the main menu and calls the right function
for each option. Quiz data and scores are stored in a MySQL database.

Run with:  python main.py
"""

import sys

from mysql.connector import Error

import database
import quiz

LEVELS = database.LEVELS  # ("easy", "medium", "hard")


# --------------------------------------------------------------------------- #
# Small input helpers (used to validate what the user types)
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


def prompt_level():
    """Ask the user to pick a difficulty level and return it as text."""
    print("\nSelect a level:")
    print("  1. Easy   2. Medium   3. Hard")
    choice = prompt_menu_choice(">>> Enter your choice (1-3): ", [1, 2, 3])
    return {"1": "easy", "2": "medium", "3": "hard"}[choice]


# --------------------------------------------------------------------------- #
# Menu actions
# --------------------------------------------------------------------------- #
def take_quiz():
    """Option 1: let a user take a quiz."""
    player_name = prompt_nonempty(">>> Enter your name: ")
    level = prompt_level()
    quiz.run_quiz(player_name, level)


def add_question():
    """Option 2 (Admin): add a new question to the database."""
    print("\n--- Add a New Question (Admin) ---")
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


def view_score_history():
    """Option 3: show recent quiz attempts."""
    print("\n--- Score History ---")
    rows = database.get_score_history(limit=20)
    if not rows:
        print("No quizzes have been taken yet.")
        return

    print(f"{'Name':<20}{'Level':<10}{'Score':<10}{'Date'}")
    print("-" * 60)
    for row in rows:
        score_text = f"{row['score']}/{row['total']}"
        taken = row["taken_at"].strftime("%Y-%m-%d %H:%M")
        print(f"{row['player_name']:<20}{row['level']:<10}{score_text:<10}{taken}")




def show_leaderboard():
    """Display top quiz players."""
    print("\n--- Leaderboard ---")

    rows = database.get_score_history(limit=100)

    if not rows:
        print("No scores available.")
        return

    ranking = {}

    for row in rows:
        name = row["player_name"]

        percentage = (row["score"] / row["total"]) * 100

        if name not in ranking:
            ranking[name] = []

        ranking[name].append(percentage)

    results = []

    for name, scores in ranking.items():
        average = sum(scores) / len(scores)
        results.append((name, average))

    results.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Player':<20}{'Average Score'}")
    print("-" * 40)

    for player, score in results[:10]:
        print(f"{player:<20}{score:.2f}%")

        
def show_menu():
    """Print the main menu."""
    print("\n===== ONLINE QUIZ SYSTEM (MySQL Edition) =====")
    print("1. Take a Quiz")
    print("2. Add a Question (Admin)")
    print("3. View Score History")
    print("4. Exit")
    print("6. Leaderboard")
    print("7. About System")

def show_about():
    print("""
--- About Online Quiz System ---

Features:
- Multiple difficulty levels
- MySQL database storage
- Score tracking
- Admin question management

Developed as a command-line quiz application.
""")


def main():
    """Set up the database, then run the main menu loop."""
    print("Welcome to the Online Quiz System!")
    print("Connecting to the database...")

    # Make sure the database and tables exist before we do anything else.
    if not database.init_database():
        print("\nCould not connect to the database. Please check your settings")
        print("in config.py / .env and make sure the MySQL server is running.")
        sys.exit(1)

    database.seed_questions_if_empty()
    print("Ready!")

    while True:
        show_menu()
        choice = prompt_menu_choice(">>> Enter your choice (1-4): ", [1, 2, 3, 4])

        try:
            if choice == "1":
                take_quiz()
            elif choice == "2":
                add_question()
            elif choice == "3":
                view_score_history()
            elif choice == "4":
                print("\nThank you for using the Online Quiz System. Goodbye!")
                break
        except Error as exc:
            # Catch any database error during an action so the app does not crash.
            print(f"\n[Database error] {exc}")
            print("Returning to the main menu.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
