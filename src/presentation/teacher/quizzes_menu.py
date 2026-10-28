from src.domain.errors import LMSError


class QuizzesMenu:
    def __init__(self, user, quiz_service, translations_menu):
        self.user = user
        self.quizzes = quiz_service
        self.translations_menu = translations_menu

    def run(self):
        while True:
            print("""
            Quiz menu
            1. Create a quiz
            2. View quizzes in a course
            3. Update a quiz
            4. Delete a quiz
            5. Manage questions
            6. Publish a quiz
            7. Release results
            8. View results report
            9. Translations
            10. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_quiz()
            elif choice == "2":
                self.view_quizzes()
            elif choice == "3":
                self.update_quiz()
            elif choice == "4":
                self.delete_quiz()
            elif choice == "5":
                self.manage_questions()
            elif choice == "6":
                self.publish_quiz()
            elif choice == "7":
                self.release_results()
            elif choice == "8":
                self.view_report()
            elif choice == "9":
                self.translations_menu.run()
            elif choice == "10":
                break
            else:
                print("Invalid choice.")

    # quizzes

    def create_quiz(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        title = input("Quiz title: ")

        raw_duration = input("Duration in minutes: ").strip()
        if not raw_duration.isdigit():
            print("Error: duration must be a number.")
            return

        try:
            quiz_id = self.quizzes.create_quiz(self.user, course_id, title, int(raw_duration))
            print(f"Quiz created with ID {quiz_id}. Add questions, then publish it.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_quizzes(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            quizzes = self.quizzes.list_quizzes(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not quizzes:
            print("This course has no quizzes yet.")
            return

        self._print_quizzes(quizzes)

    def _print_quizzes(self, quizzes):
        print(f"\n{'ID':<5}{'Title':<30}{'Minutes':<9}{'Marks':<7}{'Published':<11}{'Released'}")
        for q in quizzes:
            published = "yes" if q["is_published"] else "no"
            released = "yes" if q["results_released"] else "no"
            print(
                f"{q['id']:<5}{q['title']:<30}{q['duration']:<9}{q['total_marks']:<7}"
                f"{published:<11}{released}"
            )

    def _pick_quiz(self):
        raw_course = input("Enter the ID of the course: ")
        if not raw_course.isdigit():
            print("Error: please enter a number.")
            return None
        course_id = int(raw_course)

        try:
            quizzes = self.quizzes.list_quizzes(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return None

        if not quizzes:
            print("This course has no quizzes yet.")
            return None

        self._print_quizzes(quizzes)

        raw_quiz = input("Enter the ID of the quiz: ")
        if not raw_quiz.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((q for q in quizzes if q["id"] == int(raw_quiz)), None)
        if current is None:
            print("Error: that quiz is not in this course.")
        return current

    def update_quiz(self):
        current = self._pick_quiz()
        if current is None:
            return

        print("Press Enter to keep the current value.")
        title = input(f"Title [{current['title']}]: ") or current["title"]

        raw_duration = input(f"Duration in minutes [{current['duration']}]: ").strip()
        if raw_duration and not raw_duration.isdigit():
            print("Error: duration must be a number.")
            return
        duration = int(raw_duration) if raw_duration else current["duration"]

        try:
            self.quizzes.update_quiz(self.user, current["id"], title, duration)
            print("Quiz updated.")
        except LMSError as e:
            print(f"Error: {e}")

    def delete_quiz(self):
        current = self._pick_quiz()
        if current is None:
            return

        if input(f"Delete '{current['title']}' with all its questions and results? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.quizzes.delete_quiz(self.user, current["id"])
            print("Quiz deleted.")
        except LMSError as e:
            print(f"Error: {e}")

    def publish_quiz(self):
        current = self._pick_quiz()
        if current is None:
            return

        if input(f"Publish '{current['title']}'? Students will be able to take it. (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.quizzes.publish_quiz(self.user, current["id"])
            print("Quiz published.")
        except LMSError as e:
            print(f"Error: {e}")

    def release_results(self):
        current = self._pick_quiz()
        if current is None:
            return

        prompt = (
            f"Release results for '{current['title']}'? "
            "This closes the quiz and students will see their scores. (y/n): "
        )
        if input(prompt).lower() != "y":
            print("Cancelled.")
            return

        try:
            self.quizzes.release_results(self.user, current["id"])
            print("Results released. The quiz is now closed.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_report(self):
        current = self._pick_quiz()
        if current is None:
            return

        try:
            rows = self.quizzes.quiz_report(self.user, current["id"])
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not rows:
            print("No attempts yet.")
            return

        total = current["total_marks"]
        print(f"\nResults for '{current['title']}' (out of {total})")
        print(f"{'Student':<25}{'Attempts':<10}{'Best':<10}{'Average':<10}{'Last attempt'}")
        for r in rows:
            name = f"{r['first_name']} {r['last_name']}"
            last = r["last_attempt"].strftime("%Y-%m-%d %H:%M")
            print(f"{name:<25}{r['attempts']:<10}{str(r['best_score']):<10}{str(r['average_score']):<10}{last}")

    # questions

    def manage_questions(self):
        current = self._pick_quiz()
        if current is None:
            return

        quiz_id = current["id"]
        while True:
            print(f"""
            Questions for '{current['title']}'
            1. Add a question
            2. View questions
            3. Update a question
            4. Delete a question
            5. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_question(quiz_id)
            elif choice == "2":
                self.view_questions(quiz_id)
            elif choice == "3":
                self.update_question(quiz_id)
            elif choice == "4":
                self.delete_question(quiz_id)
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def add_question(self, quiz_id):
        text = input("Question: ")
        option_a = input("Option A: ")
        option_b = input("Option B: ")
        option_c = input("Option C: ")
        option_d = input("Option D: ")
        correct = input("Correct option (A, B, C or D): ")

        raw_marks = input("Marks (press Enter for 1): ").strip()
        if raw_marks and not raw_marks.isdigit():
            print("Error: marks must be a number.")
            return
        marks = int(raw_marks) if raw_marks else 1

        try:
            self.quizzes.add_question(
                self.user, quiz_id, text, option_a, option_b, option_c, option_d, correct, marks
            )
            print("Question added.")
        except LMSError as e:
            print(f"Error: {e}")

    def _load_questions(self, quiz_id):
        try:
            return self.quizzes.list_questions(self.user, quiz_id)
        except LMSError as e:
            print(f"Error: {e}")
            return None

    def _print_questions(self, questions):
        total = sum(q["marks"] for q in questions)
        for q in questions:
            print(f"\n[{q['id']}] {q['question_text']}  ({q['marks']} mark(s))")
            print(f"    A) {q['option_a']}")
            print(f"    B) {q['option_b']}")
            print(f"    C) {q['option_c']}")
            print(f"    D) {q['option_d']}")
            print(f"    Answer: {q['correct_option']}")
        print(f"\nTotal marks: {total}")

    def view_questions(self, quiz_id):
        questions = self._load_questions(quiz_id)
        if questions is None:
            return
        if not questions:
            print("This quiz has no questions yet.")
            return
        self._print_questions(questions)

    def _pick_question(self, quiz_id):
        questions = self._load_questions(quiz_id)
        if questions is None:
            return None
        if not questions:
            print("This quiz has no questions yet.")
            return None

        self._print_questions(questions)

        raw_id = input("Enter the ID of the question: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((q for q in questions if q["id"] == int(raw_id)), None)
        if current is None:
            print("Error: that question is not in this quiz.")
        return current

    def update_question(self, quiz_id):
        current = self._pick_question(quiz_id)
        if current is None:
            return

        print("Press Enter to keep the current value.")
        text = input(f"Question [{current['question_text']}]: ") or current["question_text"]
        option_a = input(f"Option A [{current['option_a']}]: ") or current["option_a"]
        option_b = input(f"Option B [{current['option_b']}]: ") or current["option_b"]
        option_c = input(f"Option C [{current['option_c']}]: ") or current["option_c"]
        option_d = input(f"Option D [{current['option_d']}]: ") or current["option_d"]
        correct = input(f"Correct option [{current['correct_option']}]: ") or current["correct_option"]

        raw_marks = input(f"Marks [{current['marks']}]: ").strip()
        if raw_marks and not raw_marks.isdigit():
            print("Error: marks must be a number.")
            return
        marks = int(raw_marks) if raw_marks else current["marks"]

        try:
            self.quizzes.update_question(
                self.user, current["id"], text, option_a, option_b, option_c, option_d, correct, marks
            )
            print("Question updated.")
        except LMSError as e:
            print(f"Error: {e}")

    def delete_question(self, quiz_id):
        current = self._pick_question(quiz_id)
        if current is None:
            return

        if input("Delete this question? (y/n): ").lower() != "y":
            print("Cancelled.")
            return

        try:
            self.quizzes.delete_question(self.user, current["id"])
            print("Question deleted.")
        except LMSError as e:
            print(f"Error: {e}")
