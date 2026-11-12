from src.domain.errors import LMSError

LISTEN_SECONDS = 5


class VoiceCommands:
    def __init__(self, user, voice_service, actions, numbers=None):
        self.user = user
        self.voice = voice_service
        self.actions = actions
        self.numbers = numbers or {}

    def listen_and_run(self):
        """Returns True if the user asked to log out."""
        try:
            examples = self.voice.command_examples(self.user)
        except LMSError as e:
            print(f"Error: {e}")
            return False

        print("\nSay a command, or say 'option' and its menu number:")
        for number, command in self.numbers.items():
            if command in examples:
                print(f"  option {number}: {examples[command]}")

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
            command = self.voice.understand(self.user, text, self.numbers)
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
