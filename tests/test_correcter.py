import pytest
import json
from utils.correcter import TextCorrector


def test_load_reference_words_from_json(tmp_path):
    data = ["apple", "banana", "orange", " "]
    file_path = tmp_path / "words.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    loaded_words = TextCorrector.load_reference_words_from_json(str(file_path))
    assert loaded_words == ["apple", "banana", "orange"]


def test_load_reference_words_from_json_invalid(tmp_path):
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"not": "a list"}, f)

    with pytest.raises(ValueError, match="JSON must contain a list of strings"):
        TextCorrector.load_reference_words_from_json(str(file_path))


def test_correct_text_basic():
    reference = ["apple", "banana", "orange"]
    corrector = TextCorrector(reference)

    input_text = "appl banan oranje"
    corrected = corrector.correct_text(input_text)
    assert corrected == "apple banana orange"


def test_correct_text_with_punctuation():
    reference = ["apple", "banana", "orange"]
    corrector = TextCorrector(reference)

    input_text = "appl, banan! oranje?"
    corrected = corrector.correct_text(input_text)
    assert corrected == "apple , banana ! orange ?"


def test_correct_text_no_match():
    reference = ["apple", "banana", "orange"]
    corrector = TextCorrector(reference)

    input_text = "xyz qwerty"
    corrected = corrector.correct_text(input_text)
    assert corrected == "xyz qwerty"
