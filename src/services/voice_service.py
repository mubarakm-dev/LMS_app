import re
from difflib import SequenceMatcher

from src.domain.enums import Role
from src.domain.errors import ValidationError
from src.integration import speech_to_text as default_stt
from src.integration import translator as default_translator
from src.integration import text_to_speech as default_tts
from src.services.permissions import require_role

END_MARKS = (".", "?", "!", "؟")


STUDENT_COMMANDS = {
    "browse_courses": ("Browse courses", ["browse courses", "show courses", "available courses", "all courses"], False),
    "enroll": ("Enroll in a course", ["enroll", "enrol", "join a course"], True),
    "my_courses": ("My courses", ["my courses", "enrolled courses"], False),
    "lessons": ("View lessons", ["lessons", "lesson"], False),
    "assignments": ("View assignments", ["assignments", "assignment"], False),
    "submit_assignment": ("Submit an assignment",
                          ["submit assignment", "submit an assignment", "submit my assignment"], True),
    "submissions": ("My submissions and marks",
                    ["my submissions", "submissions", "my marks", "my grades", "marks", "grades"], False),
    "quizzes": ("Quizzes", ["quizzes", "quiz", "take a quiz"], False),
    "logout": ("Log out", ["log out", "logout", "sign out", "goodbye"], True),
}

TEACHER_COMMANDS = {
    "create_course": ("Create a course", ["create course", "create a course", "new course", "add a course"], True),
    "my_courses": ("View my courses", ["my courses", "view my courses", "list my courses", "courses"], False),
    "update_course": ("Update a course", ["update course", "update a course", "edit course"], True),
    "delete_course": ("Delete a course", ["delete course", "delete a course", "remove course"], True),
    "students": ("View students in a course", ["students", "my students", "view students"], False),
    "lessons": ("Manage lessons", ["lessons", "lesson", "manage lessons"], False),
    "assignments": ("Manage assignments", ["assignments", "assignment", "manage assignments"], False),
    "quizzes": ("Manage quizzes", ["quizzes", "quiz", "manage quizzes"], False),
    "reports": ("Reports and exports", ["reports", "report", "export", "exports"], False),
    "translator": ("Voice translator", ["voice translator", "translator", "translate"], False),
    "logout": ("Log out", ["log out", "logout", "sign out", "goodbye"], True),
}

COMMANDS = {Role.STUDENT: STUDENT_COMMANDS, Role.INSTRUCTOR: TEACHER_COMMANDS}


def _sentence(text):
    text = text.strip()
    return text if text.endswith(END_MARKS) else text + "."


FUZZY_CUTOFF = 0.8


def _normalise(text):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


class VoiceService:
    def __init__(self, tts=None, stt=None, translator=None):
        self.tts = tts or default_tts
        self.stt = stt or default_stt
        self.translator = translator or default_translator

    def has_voice(self, language):
        return self.tts.has_voice(language)

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def read_question(self, acting_user, question, language="en"):
        parts = [_sentence(question["question_text"])]
        for letter in "abcd":
            parts.append(_sentence(f"{letter.upper()}. {question['option_' + letter]}"))

        self.tts.speak(" ".join(parts), language)

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def read_text(self, acting_user, text, language="en"):
        self.tts.speak(text, language)

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def listen(self, acting_user, seconds=5, language=None, on_tick=None):
        phrases = [p for entry in COMMANDS[acting_user.role].values() for p in entry[1]]
        prompt = "Voice commands: " + ", ".join(phrases) + "."
        return self.stt.listen(seconds, language, on_tick, prompt)

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def command_examples(self, acting_user):
        return {name: entry[0] for name, entry in COMMANDS[acting_user.role].items()}

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def understand(self, acting_user, text):
        words = _normalise(text).split()
        spoken = f" {' '.join(words)} "
        table = COMMANDS[acting_user.role]

        best_name, best_length = None, 0
        for name, (_, phrases, _) in table.items():
            for phrase in phrases:
                if f" {phrase} " in spoken and len(phrase) > best_length:
                    best_name, best_length = name, len(phrase)
        if best_name is not None:
            return best_name

        # nothing matched exactly: accept a close mishearing ("lesson" -> "lessen")
        best_score = FUZZY_CUTOFF
        for name, (_, phrases, _) in table.items():
            for phrase in phrases:
                size = len(phrase.split())
                for start in range(len(words) - size + 1):
                    heard = " ".join(words[start:start + size])
                    score = SequenceMatcher(None, heard, phrase).ratio()
                    if score > best_score:
                        best_name, best_score = name, score
        return best_name

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def needs_confirmation(self, acting_user, command):
        return COMMANDS[acting_user.role][command][2]

    @require_role(Role.STUDENT, Role.INSTRUCTOR)
    def command_label(self, acting_user, command):
        return COMMANDS[acting_user.role][command][0]

    @require_role(Role.INSTRUCTOR)
    def spoken_languages(self, acting_user):
        return self.translator.available_sources()

    @require_role(Role.INSTRUCTOR)
    def target_languages(self, acting_user, source):
        return self.translator.available_targets(source)

    @require_role(Role.INSTRUCTOR)
    def voice_translate(self, acting_user, source, target, seconds=8, on_tick=None):
        if target not in self.translator.available_targets(source):
            raise ValidationError(
                f"Translation from {self.translator.language_name(source)} "
                f"to {self.translator.language_name(target)} is not available."
            )

        heard, _ = self.stt.listen(seconds, source, on_tick)
        if not heard:
            return {"heard": "", "translation": ""}

        translation = self.translator.translate(heard, source, target)
        return {"heard": heard, "translation": translation}
