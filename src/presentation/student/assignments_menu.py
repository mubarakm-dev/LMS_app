from src.domain.errors import LMSError


class AssignmentsMenu:
    def __init__(self, user, assignment_service):
        self.user = user
        self.assignments = assignment_service

    def view_assignments(self):
        raw_id = input("Enter the ID of the course: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        course_id = int(raw_id)

        try:
            assignments = self.assignments.list_assignments_for_student(self.user, course_id)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not assignments:
            print("This course has no assignments yet.")
            return

        for a in assignments:
            due = a["due_date"].strftime("%Y-%m-%d") if a["due_date"] else "no deadline"
            print(f"\n[{a['id']}] {a['title']}  (due: {due}, marks: {a['max_marks']})")
            if a["description"]:
                print(a["description"])

    def submit_assignment(self):
        raw_id = input("Enter the ID of the assignment: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return
        assignment_id = int(raw_id)

        link = input("Paste the link to your work (https://...): ")

        try:
            self.assignments.submit(self.user, assignment_id, link)
            print("Submitted successfully.")
        except LMSError as e:
            print(f"Error: {e}")

    def view_my_submissions(self):
        try:
            submissions = self.assignments.my_submissions(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return

        if not submissions:
            print("You have not submitted anything yet.")
            return

        for s in submissions:
            when = s["submitted_at"].strftime("%Y-%m-%d %H:%M")
            if s["released"]:
                result = f"{s['score']}/{s['max_marks']}"
            else:
                result = "pending"

            print(f"\n{s['course_title']} / {s['assignment_title']}")
            print(f"  Submitted: {when}")
            print(f"  Link:      {s['submission_link']}")
            print(f"  Result:    {result}")
            if s["released"] and s["feedback"]:
                print(f"  Feedback:  {s['feedback']}")
