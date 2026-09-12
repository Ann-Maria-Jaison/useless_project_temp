# core/voice.py — AYYO Voice Mode TTS service using pyttsx3

import os
import re
import tempfile
from typing import List, Dict, Any, Optional

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    HAS_PYTTSX3 = False


def get_available_voices() -> List[Dict[str, Any]]:
    """
    Returns list of available system voices, indicating if a Malayalam voice is found.
    """
    if not HAS_PYTTSX3:
        return []

    voices_info = []
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices") or []

        has_ml = False
        for v in voices:
            v_id = getattr(v, "id", str(v))
            v_name = getattr(v, "name", str(v))
            langs = getattr(v, "languages", [])

            # Check if voice supports Malayalam (ml / ml_IN)
            is_ml = any("ml" in str(l).lower() for l in langs) or "malayalam" in v_name.lower()
            if is_ml:
                has_ml = True

            voices_info.append({
                "id": v_id,
                "name": v_name,
                "languages": [str(l) for l in langs],
                "is_malayalam": is_ml
            })
    except Exception:
        pass

    return voices_info


def speak_text(
    text: str,
    rate: int = 150,
    volume: int = 100,
    voice_id: Optional[str] = None
) -> bytes:
    """
    Synthesizes input text to WAV audio bytes using pyttsx3.
    """
    if not HAS_PYTTSX3:
        raise RuntimeError("pyttsx3 is not installed or available on this system.")

    if not text or not text.strip():
        raise ValueError("Text to speak cannot be empty.")

    # Clamp rate (100 - 250) and volume (0 - 100)
    rate = max(100, min(int(rate), 250))
    volume = max(0, min(int(volume), 100))

    temp_path = None
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume / 100.0)

        if voice_id:
            try:
                engine.setProperty("voice", voice_id)
            except Exception:
                pass

        fd, temp_path = tempfile.mkstemp(suffix=".wav", prefix="ayyo_tts_")
        os.close(fd)

        engine.save_to_file(text, temp_path)
        engine.runAndWait()

        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise RuntimeError("TTS failed to generate audio output file.")

        with open(temp_path, "rb") as f:
            audio_bytes = f.read()

        return audio_bytes
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def format_spoken_text(title: str = "", desc: str = "", tip: str = "") -> str:
    """
    Formats spoken text following priority order:
    Title + One-line description + Tip (skipping code blocks, hints, and technical details).
    Truncates if text is longer than ~150 chars with a soft '...ബാക്കി screen-ൽ നോക്കൂ.' suffix.
    """
    parts = []
    if title:
        parts.append(title.strip())
    if desc:
        parts.append(desc.strip())
    if tip:
        # Strip lead lightbulb if present
        clean_tip = re.sub(r"^[💡\s]+", "", tip.strip())
        parts.append(clean_tip)

    combined = ". ".join(parts)
    # Remove code snippets / markdown syntax / double spaces
    combined = re.sub(r"`[^`]*`", "", combined)
    combined = re.sub(r"\s+", " ", combined).strip()

    MAX_CHAR_LIMIT = 150
    if len(combined) > MAX_CHAR_LIMIT:
        combined = combined[:MAX_CHAR_LIMIT].rstrip(".,; ") + "... ബാക്കി screen-ൽ നോക്കൂ."

    return combined
