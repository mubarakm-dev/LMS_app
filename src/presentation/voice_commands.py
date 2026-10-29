from src.domain.errors import LMSError

LISTEN_SECONDS = 5


class VoiceCommands:
    def __init__(self, user, voice_service, actions):
        self.user = user
        self.voice = voice_service
        self.actions = actions

    def listen_and_run(self):
        """Returns True if the user asked to log out."""
        try:
            examples = self.voice.command_examples(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return False

        print("\nSay one of these:")
        for label in examples.values():
            print(f"  - {label}")

        if input(f"\nPress Enter to record for {LISTEN_SECONDS} seconds (x to cancel): ").strip().lower() == "x":
            return False

        try:
            print("Speak now...")
            text, _ = self.voice.listen(
                self.user, LISTEN_SECONDS, "en",
                on_tick=lambda left: print(f"  recording... {left}"),
            )
            if not text:
                print("I did not hear anything. Try again, a little closer to the microphone.")
                return False

            print(f"I heard: \"{text}\"")
            command = self.voice.understand(self.user, text)
            if command is None or command not in self.actions:
                print("Sorry, I did not recognise that command. Use the menu or try again.")
                return False

            label = self.voice.command_label(self.user, command)
            if self.voice.needs_confirmation(self.user, command):
                answer = input(f"Run '{label}'? (y/n): ").strip().lower()
                if answer != "y":
                    print("Cancelled.")
                    return False

            if command == "logout":
                return True

            print(f"Opening: {label}")
            self.actions[command]()
        except LMSError as e:
            print(f"Error: {e}")
        return False
