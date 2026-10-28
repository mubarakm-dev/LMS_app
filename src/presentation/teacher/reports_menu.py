from src.domain.errors import LMSError


def _num(value):
    return "-" if value is None else f"{float(value):g}"


class ReportsMenu:
    def __init__(self, user, report_service):
        self.user = user
        self.reports = report_service

    def run(self):
        while True:
            print("""
            Reports menu
            1. Course performance
            2. Student report
            3. Export quiz results (CSV)
            4. Export assignment grades (CSV)
            5. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.course_performance()
            elif choice == "2":
                self.student_report()
            elif choice == "3":
                self.export_quiz_results()
            elif choice == "4":
                self.export_assignment_grades()
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def _ask_id(self, prompt):
        raw = input(prompt).strip()
        if not raw.isdigit():
            print("Error: please enter a number.")
            return None
        return int(raw)

    def _print_course_rows(self, rows):
        print(f"\n{'ID':<5}{'Student':<25}{'Quizzes':<10}{'Assignments':<13}{'Avg score'}")
        for r in rows:
            name = f"{r['first_name']} {r['last_name']}"
            print(
                f"{r['id']:<5}{name:<25}{r['quizzes_attempted']:<10}"
                f"{r['assignments_submitted']:<13}{_num(r['avg_assignment_score'])}"
            )

    def course_performance(self):
        course_id = self._ask_id("Enter the ID of the course: ")
        if course_id is None:
            return

        try:
            rows = self.reports.course_performance(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not rows:
            print("No students are enrolled in this course yet.")
            return

        self._print_course_rows(rows)

        if input("\nExport this report to CSV? (y/n): ").lower() == "y":
            try:
                path = self.reports.export_course_performance(self.user, course_id)
                print(f"Report saved to: {path}")
            except LMSError as e:
                print(f"Error: {e}")

    def student_report(self):
        course_id = self._ask_id("Enter the ID of the course: ")
        if course_id is None:
            return

        try:
            rows = self.reports.course_performance(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not rows:
            print("No students are enrolled in this course yet.")
            return

        self._print_course_rows(rows)

        student_id = self._ask_id("Enter the ID of the student: ")
        if student_id is None:
            return

        try:
            data = self.reports.student_report(self.user, course_id, student_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        student = data["student"]
        print(f"\nReport for {student['first_name']} {student['last_name']} ({student['email']})")

        print("\nQuizzes")
        if not data["quizzes"]:
            print("  No quiz attempts yet.")
        for q in data["quizzes"]:
            last = q["last_attempt"].strftime("%Y-%m-%d %H:%M")
            print(
                f"  {q['quiz_title']:<28}attempts {q['attempts']:<3}"
                f"best {_num(q['best_score'])}/{q['total_marks']}   last {last}"
            )

        print("\nAssignments")
        if not data["assignments"]:
            print("  No submissions yet.")
        for a in data["assignments"]:
            when = a["submitted_at"].strftime("%Y-%m-%d %H:%M")
            score = f"{_num(a['score'])}/{a['max_marks']}" if a["score"] is not None else "not graded"
            released = "released" if a["released"] else "not released"
            print(f"  {a['assignment_title']:<28}{score:<14}{released:<14}submitted {when}")
            if a["feedback"]:
                print(f"      Feedback: {a['feedback']}")

    def export_quiz_results(self):
        quiz_id = self._ask_id("Enter the ID of the quiz (see 'View quizzes' for IDs): ")
        if quiz_id is None:
            return

        try:
            path = self.reports.export_quiz_results(self.user, quiz_id)
            print(f"Report saved to: {path}")
        except LMSError as e:
            print(f"Error: {e}")

    def export_assignment_grades(self):
        assignment_id = self._ask_id("Enter the ID of the assignment (see 'View assignments' for IDs): ")
        if assignment_id is None:
            return

        try:
            path = self.reports.export_assignment_grades(self.user, assignment_id)
            print(f"Report saved to: {path}")
        except LMSError as e:
            print(f"Error: {e}")
