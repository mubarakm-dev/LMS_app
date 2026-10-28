from src.domain.errors import ServiceUnavailable, ValidationError


TESTED_PAIRS = {
    ("en", "fr"),
    ("fr", "en"),
    ("en", "es"),
    ("en", "ar"),
    ("ar", "en"),
}

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "ar": "Arabic",
}


def language_name(code):
    return LANGUAGE_NAMES.get(code, code)


def available_targets(source="en"):
    return {dst: language_name(dst) for (src, dst) in sorted(TESTED_PAIRS) if src == source}


def translate(text, source, target):
    if not text or not text.strip():
        return ""

    if (source, target) not in TESTED_PAIRS:
        raise ValidationError(
            f"Translation from {language_name(source)} to {language_name(target)} "
            "is not available."
        )

    try:
        import argostranslate.translate as argos
    except ImportError:
        raise ServiceUnavailable("The translation engine (Argos Translate) is not installed.")

    try:
        installed = argos.get_installed_languages()
        from_lang = next((lang for lang in installed if lang.code == source), None)
        to_lang = next((lang for lang in installed if lang.code == target), None)
        translation = from_lang.get_translation(to_lang) if from_lang and to_lang else None

        if translation is None:
            raise ServiceUnavailable(
                f"The {language_name(source)} to {language_name(target)} "
                "language model is not installed."
            )

        return translation.translate(text)
    except ServiceUnavailable:
        raise
    except Exception:
        raise ServiceUnavailable("The translation failed. Please try again.")
