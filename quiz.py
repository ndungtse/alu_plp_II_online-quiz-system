"""Quiz-taking logic for the Online Quiz System.

This module runs a single quiz: it fetches questions for the chosen level,
asks them one at a time, checks the answers, keeps score, and saves the result.
"""

import database


def _ask_question(question, number, total):
    """Display one question and return True if the user answers correctly."""
    print(f"\nQuestion {number} of {total}:")
    print(f"  {question['question_text']}")
    print(f"     A. {question['option_a']}")
    print(f"     B. {question['option_b']}")
    print(f"     C. {question['option_c']}")
    print(f"     D. {question['option_d']}")

    # Keep asking until the user gives a valid answer (A/B/C/D).
    while True:
        answer = input(">>> Your answer (A/B/C/D): ").strip().upper()
        if answer in ("A", "B", "C", "D"):
            break
        print("    Please enter A, B, C or D.")

    correct = question["correct_option"].upper()
    if answer == correct:
        print("    OK Correct!")
        return True

    print(f"    x Wrong. The correct answer was {correct}.")
    return False


def run_quiz(player_name, level):
    """Run a full quiz for the given player and level.

    Returns a tuple (score, total). If there are no questions for the level,
    returns (0, 0).
    """
    questions = database.get_questions_by_level(level, limit=5)
    total = len(questions)

    if total == 0:
        print(f"\nSorry, there are no questions for the '{level}' level yet.")
        print("Ask an admin to add some from the main menu.")
        return 0, 0

    print(f"\n*** This is the {level.capitalize()} Level ***")
    print(f"You will be asked {total} question(s). Good luck, {player_name}!")

    score = 0
    for index, question in enumerate(questions, start=1):
        if _ask_question(question, index, total):
            score += 1

    percentage = (score / total) * 100
    print("\n" + "=" * 40)
    print(f"Quiz complete! You scored {score} out of {total} ({percentage:.0f}%).")

    database.save_score(player_name, level, score, total)
    print("Your result has been saved.")
    print("=" * 40)
    return score, total
