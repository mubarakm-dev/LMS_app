from src.presentation.student.assignments_menu import AssignmentsMenu
from src.presentation.student.courses_menu import CoursesMenu
from src.presentation.student.lessons_menu import LessonsMenu
from src.presentation.student.quizzes_menu import QuizzesMenu


class StudentMenu:
    def __init__(self, user, enrollment_service, lesson_service, assignment_service,
                 quiz_service, translation_service, voice_service):
        self.user = user
        self.courses_menu = CoursesMenu(user, enrollment_service)
        self.lessons_menu = LessonsMenu(user, lesson_service)
        self.assignments_menu = AssignmentsMenu(user, assignment_service)
        self.quizzes_menu = QuizzesMenu(user, quiz_service, translation_service, voice_service)

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the student portal")

        while True:
            print("""
            Student menu
            1. Browse courses
            2. Enroll in a course
            3. My courses
            4. View lessons for a course
            5. View assignments for a course
            6. Submit an assignment
            7. My submissions and marks
            8. Quizzes

            9. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.courses_menu.browse_courses()
            elif choice == "2":
                self.courses_menu.enroll_in_course()
            elif choice == "3":
                self.courses_menu.view_enrolled_courses()
            elif choice == "4":
                self.lessons_menu.read_course_lessons()
            elif choice == "5":
                self.assignments_menu.view_assignments()
            elif choice == "6":
                self.assignments_menu.submit_assignment()
            elif choice == "7":
                self.assignments_menu.view_my_submissions()
            elif choice == "8":
                self.quizzes_menu.run()
            elif choice == "9":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")
