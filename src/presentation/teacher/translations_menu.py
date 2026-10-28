from src.domain.errors import LMSError


class TranslationsMenu:
    def __init__(self, user, translation_service, quiz_service):
        self.user = user
        self.translations = translation_service
        self.quizzes = quiz_service

    def run(self):
        while True:
            print("""
            Translation menu
            1. Translate a whole quiz
            2. Translate one question
            3. Review a translation
            4. Edit a translation
            5. Translation status
            6. Back
            """)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.translate_quiz()
            elif choice == "2":
                self.translate_question()
            elif choice == "3":
                self.review_translation()
            elif choice == "4":
                self.edit_translation()
            elif choice == "5":
                self.show_status()
            elif choice == "6":
                break
            else:
                print("Invalid choice.")

    # helpers

    def _ask_language(self):
        languages = self.translations.supported_languages()
        listing = ", ".join(f"{code} = {name}" for code, name in languages.items())
        print(f"Languages: {listing}")

        code = input("Language code: ").strip().lower()
        if code not in languages:
            print("Error: that language is not supported.")
            return None
        return code

    def _pick_quiz(self):
        raw_course = input("Enter the ID of the course: ")
        if not raw_course.isdigit():
            print("Error: please enter a number.")
            return None

        try:
            quizzes = self.quizzes.list_quizzes(self.user, int(raw_course))
        except LMSError as e:
            print(f"Error: {e}")
            return None

        if not quizzes:
            print("This course has no quizzes yet.")
            return None

        print(f"\n{'ID':<5}{'Title':<30}{'Published'}")
        for q in quizzes:
            print(f"{q['id']:<5}{q['title']:<30}{'yes' if q['is_published'] else 'no'}")

        raw_quiz = input("Enter the ID of the quiz: ")
        if not raw_quiz.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((q for q in quizzes if q["id"] == int(raw_quiz)), None)
        if current is None:
            print("Error: that quiz is not in this course.")
        return current

    def _pick_question(self):
        quiz = self._pick_quiz()
        if quiz is None:
            return None

        try:
            questions = self.quizzes.list_questions(self.user, quiz["id"])
        except LMSError as e:
            print(f"Error: {e}")
            return None

        if not questions:
            print("This quiz has no questions yet.")
            return None

        print()
        for q in questions:
            text = q["question_text"]
            print(f"[{q['id']}] {text[:70]}{'...' if len(text) > 70 else ''}")

        raw_id = input("Enter the ID of the question: ")
        if not raw_id.isdigit():
            print("Error: please enter a number.")
            return None

        current = next((q for q in questions if q["id"] == int(raw_id)), None)
        if current is None:
            print("Error: that question is not in this quiz.")
        return current

    def _show_side_by_side(self, view, language):
        original = view["original"]
        translated = view["translation"]

        print("\nOriginal (English)")
        print(f"  {original['question_text']}")
        for letter in "abcd":
            print(f"    {letter.upper()}) {original['option_' + letter]}")
        print(f"  Answer key: {original['correct_option']} (not translated)")

        if translated is None:
            print(f"\nNo {language} translation saved yet.")
            return

        print(f"\nTranslation ({language})")
        print(f"  {translated['question_text']}")
        for letter in "abcd":
            print(f"    {letter.upper()}) {translated['option_' + letter]}")

        if view["stale"]:
            print("\nWARNING: the question was edited after this was translated. "
                  "Translate it again.")
        else:
            print("\nMachine translation: please review it before using it in an assessment.")

    # actions

    def translate_quiz(self):
        quiz = self._pick_quiz()
        if quiz is None:
            return
        language = self._ask_language()
        if language is None:
            return

        print("Translating, this can take a little while...")
        try:
            count = self.translations.translate_quiz(self.user, quiz["id"], language)
            print(f"Translated {count} question(s) into {language}. "
                  "Use 'Review a translation' to check them.")
        except LMSError as e:
            print(f"Error: {e}")

    def translate_question(self):
        question = self._pick_question()
        if question is None:
            return
        language = self._ask_language()
        if language is None:
            return

        print("Translating...")
        try:
            view = self.translations.translate_question(self.user, question["id"], language)
        except LMSError as e:
            print(f"Error: {e}")
            return
        self._show_side_by_side(view, language)

    def review_translation(self):
        question = self._pick_question()
        if question is None:
            return
        language = self._ask_language()
        if language is None:
            return

        try:
            view = self.translations.view_translation(self.user, question["id"], language)
        except LMSError as e:
            print(f"Error: {e}")
            return
        self._show_side_by_side(view, language)

    def edit_translation(self):
        question = self._pick_question()
        if question is None:
            return
        language = self._ask_language()
        if language is None:
            return

        try:
            view = self.translations.view_translation(self.user, question["id"], language)
        except LMSError as e:
            print(f"Error: {e}")
            return

        current = view["translation"]
        if current is None:
            print("There is no translation to edit yet. Translate the question first.")
            return

        print("Press Enter to keep the current text.")
        text = input(f"Question [{current['question_text']}]: ") or current["question_text"]
        options = []
        for letter in "abcd":
            old = current["option_" + letter]
            options.append(input(f"Option {letter.upper()} [{old}]: ") or old)

        try:
            self.translations.edit_translation(
                self.user, question["id"], language, text, *options
            )
            print("Translation saved.")
        except LMSError as e:
            print(f"Error: {e}")

    def show_status(self):
        quiz = self._pick_quiz()
        if quiz is None:
            return

        try:
            status = self.translations.translation_status(self.user, quiz["id"])
        except LMSError as e:
            print(f"Error: {e}")
            return

        total = status["total"]
        print(f"\nTranslations for '{quiz['title']}' ({total} question(s))")
        for code, entry in status["languages"].items():
            note = ""
            if entry["stale"]:
                note = f"   {entry['stale']} need updating"
            ready = "available to students" if total and entry["fresh"] == total else "not available yet"
            print(f"  {entry['name']:<10}{entry['fresh']}/{total} up to date{note}   ({ready})")
