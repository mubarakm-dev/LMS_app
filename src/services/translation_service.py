from src.domain.enums import Role
from src.domain.errors import NotFound, PermissionDenied, ServiceUnavailable, ValidationError
from src.integration import translator as default_translator
from src.services.permissions import require_role

SOURCE_LANGUAGE = "en"
MAX_TEXT_LENGTH = 500


class TranslationService:
    def __init__(self, translation_repo, question_repo, quiz_repo, course_repo,
                 enrollment_repo, translator=None):
        self.translation_repo = translation_repo
        self.question_repo = question_repo
        self.quiz_repo = quiz_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self.translator = translator or default_translator

    def supported_languages(self):
        return self.translator.available_targets(SOURCE_LANGUAGE)

    # teacher 

    @require_role(Role.INSTRUCTOR)
    def translate_question(self, acting_user, question_id, language):
        self._check_language(language)
        question, _ = self._get_owned_question(acting_user, question_id)
        self._translate_and_save(question, language)
        return self.view_translation(acting_user, question_id, language)

    @require_role(Role.INSTRUCTOR)
    def translate_quiz(self, acting_user, quiz_id, language):
        self._check_language(language)
        self._get_owned_quiz(acting_user, quiz_id)

        questions = self.question_repo.list_for_teacher(quiz_id)
        if not questions:
            raise ValidationError("This quiz has no questions to translate.")

        for question in questions:
            self._translate_and_save(question, language)
        return len(questions)

    @require_role(Role.INSTRUCTOR)
    def view_translation(self, acting_user, question_id, language):
        self._check_language(language)
        question, _ = self._get_owned_question(acting_user, question_id)

        saved = self.translation_repo.get(question_id, language)
        stale = saved is not None and saved["source_updated_at"] != question["updated_at"]
        return {"original": question, "translation": saved, "stale": stale}

    @require_role(Role.INSTRUCTOR)
    def edit_translation(self, acting_user, question_id, language, question_text,
                         option_a, option_b, option_c, option_d):
        self._check_language(language)
        question, _ = self._get_owned_question(acting_user, question_id)

        fields = [question_text.strip(), option_a.strip(), option_b.strip(),
                  option_c.strip(), option_d.strip()]
        if not all(fields):
            raise ValidationError("The question and all four options are required.")
        if any(len(text) > MAX_TEXT_LENGTH for text in fields[1:]):
            raise ValidationError(f"Each option must be {MAX_TEXT_LENGTH} characters or fewer.")

        self.translation_repo.save(question_id, language, *fields, question["updated_at"])

    @require_role(Role.INSTRUCTOR)
    def translation_status(self, acting_user, quiz_id):
        self._get_owned_quiz(acting_user, quiz_id)

        total = len(self.question_repo.list_for_teacher(quiz_id))
        status = {
            code: {"name": name, "fresh": 0, "stale": 0}
            for code, name in self.supported_languages().items()
        }
        for row in self.translation_repo.list_for_quiz(quiz_id):
            entry = status.get(row["language"])
            if entry is not None:
                entry["fresh" if row["is_fresh"] else "stale"] += 1

        return {"total": total, "languages": status}

    #  student 

    @require_role(Role.STUDENT)
    def available_languages(self, acting_user, quiz_id):
        self._get_published_quiz_for_student(acting_user, quiz_id)

        languages = [(SOURCE_LANGUAGE, self.translator.language_name(SOURCE_LANGUAGE))]
        complete = self._complete_languages(quiz_id)
        for code, name in self.supported_languages().items():
            if code in complete:
                languages.append((code, name))
        return languages

    @require_role(Role.STUDENT)
    def apply_language(self, acting_user, quiz_id, language, questions):
        if language == SOURCE_LANGUAGE:
            return questions

        self._get_published_quiz_for_student(acting_user, quiz_id)
        if language not in self._complete_languages(quiz_id):
            raise ValidationError("This quiz is not available in that language.")

        translated = []
        for question in questions:
            saved = self.translation_repo.get(question["id"], language)
            if saved is None:
                raise ValidationError("This quiz is not available in that language.")
            translated.append({
                **question,
                "question_text": saved["question_text"],
                "option_a": saved["option_a"],
                "option_b": saved["option_b"],
                "option_c": saved["option_c"],
                "option_d": saved["option_d"],
            })
        return translated

    #  helpers 

    def _check_language(self, language):
        if language not in self.supported_languages():
            raise ValidationError("That language is not supported.")

    def _translate_and_save(self, question, language):
        texts = [question["question_text"], question["option_a"], question["option_b"],
                 question["option_c"], question["option_d"]]
        translated = [self.translator.translate(text, SOURCE_LANGUAGE, language) for text in texts]

        if not all(t.strip() for t in translated):
            raise ServiceUnavailable("The translation came back empty. Please try again.")

        translated[1:] = [t[:MAX_TEXT_LENGTH] for t in translated[1:]]
        self.translation_repo.save(question["id"], language, *translated, question["updated_at"])

    def _complete_languages(self, quiz_id):
        total = len(self.question_repo.list_for_student(quiz_id))
        fresh = {}
        for row in self.translation_repo.list_for_quiz(quiz_id):
            if row["is_fresh"]:
                fresh[row["language"]] = fresh.get(row["language"], 0) + 1
        return {code for code, count in fresh.items() if total > 0 and count == total}

    def _get_published_quiz_for_student(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None or not quiz["is_published"]:
            raise NotFound("Quiz is not found")
        if not self.enrollment_repo.exists(acting_user.id, quiz["course_id"]):
            raise PermissionDenied("Enroll in this course to take its quizzes.")
        return quiz

    def _get_owned_quiz(self, acting_user, quiz_id):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if quiz is None:
            raise NotFound("Quiz is not found")
        course = self.course_repo.get_by_id(quiz["course_id"])
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] != acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return quiz

    def _get_owned_question(self, acting_user, question_id):
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise NotFound("Question is not found")
        quiz = self._get_owned_quiz(acting_user, question["quiz_id"])
        return question, quiz
