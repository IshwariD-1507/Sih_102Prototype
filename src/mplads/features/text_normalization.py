import re
from functools import lru_cache

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from ai4bharat.transliteration import XlitEngine


# ============================================================
# Model configuration
# ============================================================

INDICTRANS_MODEL = "ai4bharat/indictrans2-indic-en-1B"


# IndicTrans2 language codes
LANGUAGE_CODES = {
    "Hindi": "hin_Deva",
    "Gujarati": "guj_Gujr",
    "Marathi": "mar_Deva",
}


# ============================================================
# IndicXlit
# ============================================================

@lru_cache(maxsize=None)
def get_transliterator(language_code):
    """
    Load AI4Bharat IndicXlit transliteration engine.
    """

    return XlitEngine(
        language_code,
        beam_width=10,
        rescore=True
    )


def transliterate_roman_text(text, language_code):
    """
    Convert Romanized Indic text into native Indic script
    using AI4Bharat IndicXlit.
    """

    if not text:
        return ""

    engine = get_transliterator(language_code)

    words = text.split()
    converted_words = []

    for word in words:

        # Keep numbers/punctuation unchanged
        if not re.search(r"[A-Za-z]", word):
            converted_words.append(word)
            continue

        try:
            result = engine.translit_word(
                word,
                topk=1
            )

            if isinstance(result, dict):
                candidates = result.get(
                    language_code,
                    []
                )
            else:
                candidates = result

            if candidates:
                converted_words.append(
                    candidates[0]
                )
            else:
                converted_words.append(word)

        except Exception:
            # Preserve original text if transliteration fails
            converted_words.append(word)

    return " ".join(converted_words)


# ============================================================
# IndicTrans2
# ============================================================

@lru_cache(maxsize=1)
def get_translation_model():
    """
    Load the AI4Bharat IndicTrans2 Indic → English model.

    The model is loaded only once and then reused.
    """

    tokenizer = AutoTokenizer.from_pretrained(
        INDICTRANS_MODEL,
        trust_remote_code=True
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        INDICTRANS_MODEL,
        trust_remote_code=True,
        device_map="auto"
    )

    model.eval()

    return tokenizer, model


def translate_to_english(
    text,
    source_language
):
    """
    Translate an Indic-language sentence into English
    using IndicTrans2.
    """

    if not text:
        return ""

    if source_language not in LANGUAGE_CODES:
        return text

    source_code = LANGUAGE_CODES[
        source_language
    ]

    tokenizer, model = get_translation_model()

    try:

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        # Move tensors to the same device as the model
        if hasattr(model, "device"):
            inputs = {
                key: value.to(model.device)
                for key, value in inputs.items()
            }

        with torch.no_grad():

            generated_tokens = model.generate(
                **inputs,
                max_length=256,
                num_beams=4,
                early_stopping=True
            )

        translated = tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )

        if translated:
            return translated[0].strip()

    except Exception:
        pass

    # Never destroy the original representation
    return text


# ============================================================
# Script detection
# ============================================================

def is_latin_text(text):
    """
    Check whether text contains Latin/Roman characters.
    """

    if not text:
        return False

    return bool(
        re.search(
            r"[A-Za-z]",
            str(text)
        )
    )


def is_devanagari_text(text):
    """
    Check whether text contains Devanagari characters.
    """

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0900-\u097F]",
            str(text)
        )
    )


def is_gujarati_text(text):
    """
    Check whether text contains Gujarati characters.
    """

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0A80-\u0AFF]",
            str(text)
        )
    )


def detect_script(text):
    """
    Detect the script used in a work description.

    Returns:
        Latin
        Devanagari
        Gujarati
        Mixed
        Unknown
    """

    if not text:
        return "Unknown"

    detected = []

    if is_latin_text(text):
        detected.append("Latin")

    if is_devanagari_text(text):
        detected.append("Devanagari")

    if is_gujarati_text(text):
        detected.append("Gujarati")

    if not detected:
        return "Unknown"

    if len(detected) > 1:
        return "Mixed"

    return detected[0]


# ============================================================
# Normalization
# ============================================================

def normalize_description(
    text,
    language_name=None
):
    """
    Convert a work description into a representation
    suitable for semantic comparison.

    Pipeline:

        Romanized Indic
            ↓
        IndicXlit
            ↓
        Native Indic script
            ↓
        IndicTrans2
            ↓
        English

    English descriptions are returned unchanged.
    """

    if not text:
        return ""

    original_text = str(text).strip()

    if not original_text:
        return ""

    script = detect_script(
        original_text
    )

    # --------------------------------------------------------
    # Already English / Latin
    # --------------------------------------------------------

    if script == "Latin":

        if language_name in LANGUAGE_CODES:

            native_text = transliterate_roman_text(
                original_text,
                LANGUAGE_CODES[language_name]
            )

            return translate_to_english(
                native_text,
                language_name
            )

        return original_text

    # --------------------------------------------------------
    # Native Hindi / Marathi
    # --------------------------------------------------------

    if script == "Devanagari":

        if language_name in {
            "Hindi",
            "Marathi"
        }:

            return translate_to_english(
                original_text,
                language_name
            )

        return original_text

    # --------------------------------------------------------
    # Native Gujarati
    # --------------------------------------------------------

    if script == "Gujarati":

        if language_name == "Gujarati":

            return translate_to_english(
                original_text,
                "Gujarati"
            )

        return original_text

    # --------------------------------------------------------
    # Mixed / unknown
    # --------------------------------------------------------

    return original_text


# ============================================================
# Project-level helper
# ============================================================

def normalize_for_embedding(
    text,
    language_name=None
):
    """
    Prepare a work description for semantic similarity.

    The original description is never modified.
    """

    return normalize_description(
        text,
        language_name
    )