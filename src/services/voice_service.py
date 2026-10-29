from src.domain.enums import Role
from src.integration import text_to_speech as default_tts
from src.services.permissions import require_role

END_MARKS = (".", "?", "!", "؟")


def _sentence(text):
    text = text.strip()
    return text if text.endswith(END_MARKS) else text + "."


class VoiceService:
    def __init__(self, tts=None):
        self.tts = tts or default_tts

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
