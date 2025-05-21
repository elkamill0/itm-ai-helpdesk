import difflib
import json
import re


class TextCorrector:
    def __init__(self, reference_words: list[str]):
        self.reference_words = reference_words

    @staticmethod
    def load_reference_words_from_json(path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return [str(word).strip() for word in data if str(word).strip()]
            raise ValueError("JSON must contain a list of strings")

    def correct_text(self, input_text: str) -> str:
        tokens = re.findall(r"\w+|[^\w\s]", input_text, re.UNICODE)
        corrected_tokens = []

        for token in tokens:
            if token.isalpha():
                match = difflib.get_close_matches(
                    token, self.reference_words, n=1, cutoff=0.5
                )
                corrected_tokens.append(match[0] if match else token)
            else:
                corrected_tokens.append(token)

        return " ".join(corrected_tokens)


if __name__ == "__main__":
    dictionary = TextCorrector.load_reference_words_from_json(
        "../resources/output.json"
    )

    input_text = "GRUPA AE procedure 'GG_NORMĄ MAT_TREF Tine: 98, cal: 7"  # <- wynik z converter.py
    corrector = TextCorrector(dictionary)
    corrected_text = corrector.correct_text(input_text)

    print("Corrected text:")
    print(corrected_text)
