from src.domain.enums import Role
from src.presentation.admin_menu import AdminMenu
from src.presentation.auth_menu import AuthMenu
from src.presentation.student.student_menu import StudentMenu
from src.presentation.teacher.teacher_menu import TeacherMenu


class App:
    def __init__(
        self,
        auth_service,
        user_service,
        course_service,
        enrollment_service,
        lesson_service,
        assignment_service,
        quiz_service,
        admin_report_service,
        teacher_report_service,
        translation_service,
        voice_service,
    ):
        self.auth_menu = AuthMenu(auth_service)
        self.users = user_service
        self.courses = course_service
        self.enrollments = enrollment_service
        self.lessons = lesson_service
        self.assignments = assignment_service
        self.quizzes = quiz_service
        self.admin_reports = admin_report_service
        self.teacher_reports = teacher_report_service
        self.translations = translation_service
        self.voice = voice_service

    def main_menu(self):
        while True:
            print("""Welcome to SQI Learning Centre

            1. Register
            2. Login
            3. Exit
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.auth_menu.register()
            elif choice == "2":
                user = self.auth_menu.login()
                if user is not None:
                    self.open_role_menu(user)
            elif choice == "3":
                print("Thank you for using SQI LMS")
                break
            else:
                print("Invalid choice.")

    def open_role_menu(self, user):
        if user.role == Role.STUDENT:
            StudentMenu(
                user, self.enrollments, self.lessons, self.assignments, self.quizzes,
                self.translations, self.voice
            ).run()
        elif user.role == Role.INSTRUCTOR:
            TeacherMenu(
                user, self.courses, self.lessons, self.assignments, self.quizzes,
                self.teacher_reports, self.translations, self.voice
            ).run()
        elif user.role == Role.ADMIN:
            AdminMenu(user, self.users, self.admin_reports).run()
