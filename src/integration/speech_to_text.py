import time

from src.domain.errors import ServiceUnavailable

SAMPLE_RATE = 16000
SILENCE_LEVEL = 0.01
MODEL_NAME = "base"

_model = None


def _load_model():
    global _model
    if _model is None:
        try:
            import whisper

            _model = whisper.load_model(MODEL_NAME)
        except Exception:
            raise ServiceUnavailable(
                "Speech recognition is not available. Check that Whisper is installed."
            )
    return _model


def record(seconds, on_tick=None):
    import sounddevice as sd

    try:
        audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                       channels=1, dtype="float32")
        for left in range(seconds, 0, -1):
            if on_tick is not None:
                on_tick(left)
            time.sleep(1)
        sd.wait()
    except Exception:
        raise ServiceUnavailable(
            "Could not use the microphone. Check that it is plugged in and allowed."
        )
    finally:
        try:
            sd.stop()
        except Exception:
            pass

    return audio.flatten()


def transcribe(audio, language=None, prompt=None):
    if float(abs(audio).max()) < SILENCE_LEVEL:
        return "", language

    model = _load_model()
    try:
        result = model.transcribe(audio, language=language, fp16=False, initial_prompt=prompt)
    except Exception:
        raise ServiceUnavailable("Could not understand the recording. Please try again.")

    return result["text"].strip(), result["language"]


def listen(seconds=5, language=None, on_tick=None, prompt=None):
    audio = record(seconds, on_tick)
    return transcribe(audio, language, prompt)
