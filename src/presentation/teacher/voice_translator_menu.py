from src.domain.errors import LMSError

RECORD_SECONDS = 8


class VoiceTranslatorMenu:
    def __init__(self, user, voice_service):
        self.user = user
        self.voice = voice_service

    def _choose(self, prompt, languages):
        listing = ", ".join(f"{code} = {name}" for code, name in languages.items())
        print(f"Languages: {listing}")
        code = input(prompt).strip().lower()
        if code not in languages:
            print("Error: that language is not supported.")
            return None
        return code

    def run(self):
        try:
            sources = self.voice.spoken_languages(self.user)
            source = self._choose("I will speak in (language code): ", sources)
            if source is None:
                return
            targets = self.voice.target_languages(self.user, source)
            target = self._choose("Translate into (language code): ", targets)
            if target is None:
                return
        except LMSError as e:
            print(f"Error: {e}")
            return

        while True:
            if input(f"\nPress Enter to record for {RECORD_SECONDS} seconds (x to stop): ").strip().lower() == "x":
                return

            try:
                print("Speak now...")
                result = self.voice.voice_translate(
                    self.user, source, target, RECORD_SECONDS,
                    on_tick=lambda left: print(f"  recording... {left}"),
                )
                if not result["heard"]:
                    print("I did not hear anything. Try again, a little closer to the microphone.")
                    continue

                print(f"\nI heard:     {result['heard']}")
                print(f"Translation: {result['translation']}")

                if self.voice.has_voice(target):
                    print("Speaking...")
                    self.voice.read_text(self.user, result["translation"], target)
            except LMSError as e:
                print(f"Error: {e}")
