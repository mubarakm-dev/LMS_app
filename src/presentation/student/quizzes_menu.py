import time

from src.domain.errors import LMSError

VALID_ANSWERS = ("A", "B", "C", "D")


def _fmt(score):
    return f"{float(score):g}"


class QuizzesMenu:
    def __init__(self, user, quiz_service):
        self.user = user
        self.quizzes = quiz_service

    def run(self):
        while True:
            print("""
            Quiz menu
            1. View quizzes in a course
            2. Take a quiz
            3. My quiz results
            4. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_quizzes()
            elif choice == "2":
                self.take_quiz()
            elif choice == "3":
                self.view_results()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    def view_quizzes(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            quizzes = self.quizzes.list_quizzes_for_student(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not quizzes:
            print("This course has no quizzes available yet.")
            return

        print(f"\n{'ID':<5}{'Title':<30}{'Minutes':<9}{'Marks':<7}{'Status'}")
        for q in quizzes:
            status = "closed" if q["results_released"] else "open"
            print(f"{q['id']:<5}{q['title']:<30}{q['duration']:<9}{q['total_marks']:<7}{status}")

    def take_quiz(self):
        raw_id = input("Enter the ID of the quiz: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        quiz_id = int(raw_id)

        print("The timer starts as soon as you begin. Press Enter on a question to skip it.")
        if input("Start now? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            data = self.quizzes.start_quiz(self.user, quiz_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        quiz = data["quiz"]
        questions = data["questions"]
        limit_seconds = quiz["duration"] * 60

        print(f"\n{quiz['title']}: {len(questions)} question(s), "
              f"{quiz['total_marks']} mark(s), {quiz['duration']} minute(s).")

        started = time.monotonic()
        answers = {}
        time_up = False

        for number, q in enumerate(questions, start=1):
            left = limit_seconds - (time.monotonic() - started)
            if left <= 0:
                time_up = True
                break

            print(f"\nQuestion {number} of {len(questions)}  ({q['marks']} mark(s))"
                  f"   Time left: {int(left // 60)}:{int(left % 60):02d}")
            print(q["question_text"])
            print(f"  A) {q['option_a']}")
            print(f"  B) {q['option_b']}")
            print(f"  C) {q['option_c']}")
            print(f"  D) {q['option_d']}")

            answer = self._ask_answer()
            if answer is not None:
                answers[q["id"]] = answer

        if time_up:
            print("\nTime is up! Submitting the answers you have given.")
        elif input("\nSubmit your answers? (y/n): ").lower() != "y":
            print("Attempt discarded.")
            return

        try:
            attempt_number = self.quizzes.submit_quiz(self.user, quiz_id, answers)
        except LMSError as e:
            print(f"Error: {e}")
            return

        print(f"Your answers were submitted (attempt {attempt_number}).")
        print("Your result will appear once your teacher releases it.")

    def _ask_answer(self):
        while True:
            raw = input("Your answer (A, B, C or D, Enter to skip): ").strip().upper()
            if raw == "":
                return None
            if raw in VALID_ANSWERS:
                return raw
            print("Please enter A, B, C or D.")

    def view_results(self):
        try:
            rows = self.quizzes.my_results(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not rows:
            print("You have not attempted any quizzes yet.")
            return

        print(f"\n{'ID':<5}{'Course':<22}{'Quiz':<25}{'Attempts':<10}{'Best score'}")
        for r in rows:
            if r["results_released"]:
                best = f"{_fmt(r['best_score'])}/{r['total_marks']}"
            else:
                best = "pending"
            print(f"{r['quiz_id']:<5}{r['course_title']:<22}{r['quiz_title']:<25}{r['attempts']:<10}{best}")

        raw_id = input("\nEnter a quiz ID to see its attempts (or press Enter to go back): ").strip()
        if not raw_id:
            return
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return

        self._show_attempts(int(raw_id))

    def _show_attempts(self, quiz_id):
        try:
            data = self.quizzes.my_attempts(self.user, quiz_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        quiz = data["quiz"]
        attempts = data["attempts"]

        if not attempts:
            print("You have no attempts for that quiz.")
            return

        print(f"\n{quiz['title']}")
        for number, attempt in enumerate(attempts, start=1):
            when = attempt["attempted_at"].strftime("%Y-%m-%d %H:%M")
            if attempt["score"] is None:
                result = "pending"
            else:
                result = f"{_fmt(attempt['score'])}/{quiz['total_marks']}"
            print(f"  Attempt {number}   {when}   {result}")

        if data["best_score"] is not None:
            print(f"  Best score: {_fmt(data['best_score'])}/{quiz['total_marks']}")
