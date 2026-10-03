# Common ligature mis-extractions seen from certain PDF generators (e.g. Canva exports).
# PyMuPDF sometimes renders these ligatures as the wrong Unicode character.
LIGATURE_FIXES = {
    "Ɵ": "ti",
    "Ü": "k",  # seen in "SÜills" -> "Skills" in some exports
    "Οͺ": "ffi",
}


def clean_extracted_text(text: str) -> str:
    """Applies light, known-safe fixes for common PDF ligature extraction artifacts.
    This is a heuristic, not a guarantee, Gemini is also instructed to use judgment
    with slightly garbled text."""
    cleaned = text
    for broken, fixed in LIGATURE_FIXES.items():
        cleaned = cleaned.replace(broken, fixed)
    return cleaned