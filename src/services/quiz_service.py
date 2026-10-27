from datetime import datetime, timedelta

from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ValidationError
from src.services.permissions import require_role

VALID_OPTIONS = ("A", "B", "C", "D")
MAX_OPTION_LENGTH = 255
GRACE_SECONDS = 10


class QuizService:
    def __init__(self, quiz_repo, question_repo, result_repo, course_repo, enrollment_repo):
        self.quiz_repo = quiz_repo
        self.question_repo = question_repo
        self.result_repo = result_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self._started = {}

    # teacher: quizzes

    @require_role(Role.INSTRUCTOR)
    def create_quiz(self, acting_user, course_id, title, duration):
        title = title.strip()
        if not title:
            raise ValidationError("Quiz title is required.")
        self._check_duration(duration)

        self._get_owned_course(acting_user, course_id)

        return self.quiz_repo.create(course_id, title, duration)

    @require_role(Role.INSTRUCTOR)
    def list_quizzes(self, acting_user, course_id):
        self._get_owned_course(acting_user, course_id)
        return self.quiz_repo.list_by_course(course_id)

    @require_role(Role.INSTRUCTOR)
    def update_quiz(self, acting_user, quiz_id, title, duration):
        title = title.strip()
        if not title:
            raise ValidationError("Quiz title is required.")
        self._check_duration(duration)

        quiz = self._get_owned_quiz(acting_user, quiz_id)
        self._ensure_open(quiz)

        self.quiz_repo.update(quiz_id, title, duration)

    @require_role(Role.INSTRUCTOR)
    def delete_quiz(self, acting_user, quiz_id):
        self._get_owned_quiz(acting_user, quiz_id)
        self.quiz_repo.delete(quiz_id)

    @require_role(Role.INSTRUCTOR)
    def publish_quiz(self, acting_user, quiz_id):
        quiz = self._get_owned_quiz(acting_user, quiz_id)

        if quiz["is_published"]:
            raise ValidationError("This quiz is already published.")
        if not self.question_repo.list_for_teacher(quiz_id):
            raise ValidationError("Add at least one question before publishing.")

        self.quiz_repo.set_published(quiz_id, True)

    @require_role(Role.INSTRUCTOR)
    def release_results(self, acting_user, quiz_id):
        quiz = self._get_owned_quiz(acting_user, quiz_id)

        if not quiz["is_published"]:
            raise ValidationError("Publish the quiz before releasing results.")
        if quiz["results_released"]:
            raise ValidationError("Results have already been released.")

        self.quiz_repo.set_results_released(quiz_id)

    @require_role(Role.INSTRUCTOR)
    def quiz_report(self, acting_user, quiz_id):
        self._get_owned_quiz(acting_user, quiz_id)
        return self.result_repo.summary_for_quiz(quiz_id)

    # teacher: questions

    @require_role(Role.INSTRUCTOR)
    def add_question(self, acting_user, quiz_id, question_text, option_a, option_b,
                     option_c, option_d, correct_option, marks):
        fields = self._clean_question(question_text, option_a, option_b, option_c,
                                      option_d, correct_option, marks)

        quiz = self._get_owned_quiz(acting_user, quiz_id)
        self._ensure_open(quiz)

        question_id = self.question_repo.create(quiz_id, *fields)
        self.quiz_repo.refresh_total_marks(quiz_id)
        return question_id

    @require_role(Role.INSTRUCTOR)
    def list_questions(self, acting_user, quiz_id):
        self._get_owned_quiz(acting_user, quiz_id)
        return self.question_repo.list_for_teacher(quiz_id)

    @require_role(Role.INSTRUCTOR)
    def update_question(self, acting_user, question_id, question_text, option_a, option_b,
                        option_c, option_d, correct_option, marks):
        fields = self._clean_question(question_text, option_a, option_b, option_c,
                                      option_d, correct_option, marks)

        question = self._get_question(question_id)
        quiz = self._get_owned_quiz(acting_user, question["quiz_id"])
        self._ensure_open(quiz)

        self.question_repo.update(question_id, *fields)
        self.quiz_repo.refresh_total_marks(question["quiz_id"])

    @require_role(Role.INSTRUCTOR)
    def delete_question(self, acting_user, question_id):
        question = self._get_question(question_id)
        quiz = self._get_owned_quiz(acting_user, question["quiz_id"])
        self._ensure_open(quiz)

        self.question_repo.delete(question_id)
        self.quiz_repo.refresh_total_marks(question["quiz_id"])

    # student

    @require_role(Role.STUDENT)
    def list_quizzes_for_student(self, acting_user, course_id):
        if self.course_repo.get_by_id(course_id) is None:
            raise NotFound("Course is not found")

        if not self.enrollment_repo.exists(acting_user.id, course_id):
            raise PermissionDenied("Enroll in this course to see its quizzes.")

        return self.quiz_repo.list_published_by_course(course_id)

    @require_role(Role.STUDENT)
    def start_quiz(self, acting_user, quiz_id):
        quiz = self._get_available_quiz(acting_user, quiz_id)

        questions = self.question_repo.list_for_student(quiz_id)
        if not questions:
            raise ValidationError("This quiz has no questions yet.")

        self._started[(acting_user.id, quiz_id)] = datetime.now()

        return {
            "quiz": {
                "id": quiz["id"],
                "title": quiz["title"],
                "duration": quiz["duration"],
                "total_marks": quiz["total_marks"],
            },
            "questions": questions,
        }

    @require_role(Role.STUDENT)
    def submit_quiz(self, acting_user, quiz_id, answers, language="en"):
        quiz = self._get_available_quiz(acting_user, quiz_id)

        started = self._started.pop((acting_user.id, quiz_id), None)
        if started is None:
            raise ValidationError("Start the quiz before submitting.")

        allowed = timedelta(minutes=quiz["duration"], seconds=GRACE_SECONDS)
        if datetime.now() - started > allowed:
            raise ValidationError("Time is up. This attempt was not recorded.")

        score = 0
        for question_id, key in self.question_repo.get_answer_key(quiz_id).items():
            chosen = answers.get(question_id)
            if isinstance(chosen, str) and chosen.strip().upper() == key["correct_option"]:
                score += key["marks"]

        self.result_repo.create(quiz_id, acting_user.id, score, language)
        return self.result_repo.attempt_count(acting_user.id, quiz_id)

    @require_role(Role.STUDENT)
    def my_results(self, acting_user):
        rows = self.result_repo.summary_by_student(acting_user.id)
        for row in rows:
            if not row["results_released"]:
                row["best_score"] = None
        return rows

    @require_role(Role.STUDENT)
    def my_attempts(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None:
            raise NotFound("Quiz is not found")

        attempts = self.result_repo.list_by_student_and_quiz(acting_user.id, quiz_id)
        if not quiz["results_released"]:
            for attempt in attempts:
                attempt["score"] = None
            return {"quiz": quiz, "attempts": attempts, "best_score": None}

        best = self.result_repo.best_score(acting_user.id, quiz_id)
        return {"quiz": quiz, "attempts": attempts, "best_score": best}

    #  helpers

    def _get_available_quiz(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None or not quiz["is_published"]:
            raise NotFound("Quiz is not found")

        if not self.enrollment_repo.exists(acting_user.id, quiz["course_id"]):
            raise PermissionDenied("Enroll in this course to take its quizzes.")

        if quiz["results_released"]:
            raise ValidationError("This quiz is closed because its results were released.")

        return quiz

    def _check_duration(self, duration):
        if duration < 1:
            raise ValidationError("Duration must be at least 1 minute.")

    def _clean_question(self, question_text, option_a, option_b, option_c, option_d,
                        correct_option, marks):
        question_text = question_text.strip()
        if not question_text:
            raise ValidationError("Question text is required.")

        options = [option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip()]
        if not all(options):
            raise ValidationError("All four answer options are required.")
        if any(len(option) > MAX_OPTION_LENGTH for option in options):
            raise ValidationError(f"Each option must be {MAX_OPTION_LENGTH} characters or fewer.")
        if len(set(option.lower() for option in options)) < 4:
            raise ValidationError("The four answer options must be different from each other.")

        correct_option = correct_option.strip().upper()
        if correct_option not in VALID_OPTIONS:
            raise ValidationError("The correct option must be A, B, C or D.")

        if marks < 1:
            raise ValidationError("Marks must be 1 or higher.")

        return (question_text, *options, correct_option, marks)

    def _ensure_open(self, quiz):
        if quiz["results_released"]:
            raise ValidationError("This quiz is closed because its results were released.")

    def _get_question(self, question_id):
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise NotFound("Question is not found")
        return question

    def _get_owned_course(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] != acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return course

    def _get_owned_quiz(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None:
            raise NotFound("Quiz is not found")
        self._get_owned_course(acting_user, quiz["course_id"])
        return quiz
