from app.services.text_cleanup import clean_extracted_text


def test_real_letters_are_not_changed():
    text = "\u00dcBER M\u00fcller \u00dcnal"

    assert clean_extracted_text(text) == text


def test_the_known_broken_ligature_is_still_repaired():
    assert clean_extracted_text("comple\u019fng") == "completing"