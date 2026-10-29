import asyncio
import os
import tempfile

from src.domain.errors import ServiceUnavailable, ValidationError
from src.integration.translator import language_name

VOICES = {
    "en": "en-US-AriaNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "ar": "ar-SA-HamedNeural",
}


def has_voice(language):
    return language in VOICES


async def _synthesize(text, voice, path):
    import edge_tts

    await edge_tts.Communicate(text=text, voice=voice).save(path)


def _play(path):
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    finally:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except pygame.error:
            pass
        pygame.mixer.quit()


def speak(text, language):
    voice = VOICES.get(language)
    if voice is None:
        raise ValidationError(f"No voice is available for {language_name(language)}.")

    if not text or not text.strip():
        return

    fd, path = tempfile.mkstemp(prefix="lms_speech_", suffix=".mp3")
    os.close(fd)

    try:
        try:
            asyncio.run(_synthesize(text, voice, path))
        except Exception:
            raise ServiceUnavailable(
                "Could not generate speech. Check your internet connection and try again."
            )

        if os.path.getsize(path) == 0:
            raise ServiceUnavailable("No audio was produced. Please try again.")

        try:
            _play(path)
        except Exception:
            raise ServiceUnavailable("Could not play audio on this computer.")
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
