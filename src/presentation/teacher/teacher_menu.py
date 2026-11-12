from src.domain.errors import AuthError
from src.presentation.teacher.assignments_menu import AssignmentsMenu
from src.presentation.teacher.courses_menu import CoursesMenu
from src.presentation.teacher.lessons_menu import LessonsMenu
from src.presentation.teacher.quizzes_menu import QuizzesMenu
from src.presentation.teacher.reports_menu import ReportsMenu
from src.presentation.teacher.translations_menu import TranslationsMenu
from src.presentation.teacher.voice_translator_menu import VoiceTranslatorMenu
from src.presentation.profile_menu import ProfileMenu
from src.presentation.voice_commands import VoiceCommands


class TeacherMenu:
    def __init__(self, user, course_service, lesson_service, assignment_service,
                 quiz_service, report_service, translation_service, voice_service, user_service):
        self.user = user
        self.users = user_service
        self.courses_menu = CoursesMenu(user, course_service)
        self.lessons_menu = LessonsMenu(user, lesson_service)
        self.assignments_menu = AssignmentsMenu(user, assignment_service)
        translations_menu = TranslationsMenu(user, translation_service, quiz_service, voice_service)
        self.quizzes_menu = QuizzesMenu(user, quiz_service, translations_menu)
        self.reports_menu = ReportsMenu(user, report_service)
        self.profile_menu = ProfileMenu(user, user_service)
        self.voice_translator_menu = VoiceTranslatorMenu(user, voice_service)
        self.voice_commands = VoiceCommands(user, voice_service, {
            "create_course": self.courses_menu.create_course,
            "my_courses": self.courses_menu.view_my_courses,
            "update_course": self.courses_menu.update_course,
            "delete_course": self.courses_menu.delete_course,
            "students": self.courses_menu.view_course_students,
            "lessons": self.lessons_menu.run,
            "assignments": self.assignments_menu.run,
            "quizzes": self.quizzes_menu.run,
            "reports": self.reports_menu.run,
            "profile": self.profile_menu.run,
            "translator": self.voice_translator_menu.run,
            "logout": None,
        }, numbers={
            1: "create_course", 2: "my_courses", 3: "update_course", 4: "delete_course",
            5: "students", 6: "lessons", 7: "assignments", 8: "quizzes", 9: "reports",
            11: "translator", 12: "profile", 13: "logout",
        })

    def run(self):
        print(f"Welcome {self.user.first_name} {self.user.last_name} to the instructor portal")

        while True:
            try:
                self.users.check_session(self.user)
            except AuthError as e:
                print(f"{e}")
                break

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

            10. Speak a command
            11. Voice translator
            12. My profile
            13. Logout
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
                if self.voice_commands.listen_and_run():
                    print("Logged out.")
                    break
            elif choice == "11":
                self.voice_translator_menu.run()
            elif choice == "12":
                self.profile_menu.run()
            elif choice == "13":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")
