from src.presentation.teacher.assignments_menu import AssignmentsMenu
from src.presentation.teacher.courses_menu import CoursesMenu
from src.presentation.teacher.lessons_menu import LessonsMenu
from src.presentation.teacher.quizzes_menu import QuizzesMenu
from src.presentation.teacher.reports_menu import ReportsMenu


class TeacherMenu:
    def __init__(self, user, course_service, lesson_service, assignment_service,
                 quiz_service, report_service):
        self.user = user
        self.courses_menu = CoursesMenu(user, course_service)
        self.lessons_menu = LessonsMenu(user, lesson_service)
        self.assignments_menu = AssignmentsMenu(user, assignment_service)
        self.quizzes_menu = QuizzesMenu(user, quiz_service)
        self.reports_menu = ReportsMenu(user, report_service)

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the instructor portal")

        while True:
            print("""
            Instructor menu
            1. Create a course
            2. View my courses
            3. Update a course
            4. Delete a course
            5. View students in a course
            6. Manage lessons
            7. Manage assignments
            8. Manage quizzes
            9. Reports and exports

            10. Logout
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.courses_menu.create_course()
            elif choice == "2":
                self.courses_menu.view_my_courses()
            elif choice == "3":
                self.courses_menu.update_course()
            elif choice == "4":
                self.courses_menu.delete_course()
            elif choice == "5":
                self.courses_menu.view_course_students()
            elif choice == "6":
                self.lessons_menu.run()
            elif choice == "7":
                self.assignments_menu.run()
            elif choice == "8":
                self.quizzes_menu.run()
            elif choice == "9":
                self.reports_menu.run()
            elif choice == "10":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")
