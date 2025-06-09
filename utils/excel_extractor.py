import os
import pandas as pd
import json
import re


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, "resources", "output.json")


class ExcelConverter:
    def __init__(
        self,
        excel_filename,
        output_filename=DEFAULT_OUTPUT_PATH,
        ignored_columns=None,
    ):
        self.excel_filename = excel_filename
        self.output_filename = output_filename
        self.ignored_columns = ignored_columns if ignored_columns is not None else []
        self.combined_text = ""
        self.unique_words = []

    def load_and_process_excel(self):
        df = pd.read_excel(self.excel_filename, sheet_name=None)

        for sheet in df.values():
            sheet = sheet.drop(
                columns=[col for col in sheet.columns if col in self.ignored_columns],
                errors="ignore",
            )

            for column in sheet.columns:
                self.combined_text += " ".join(sheet[column].astype(str)) + " "

    def extract_unique_words(self):
        words = re.findall(r"\b\w+\b", self.combined_text.lower())
        self.unique_words = sorted(set(words), key=words.index)

    def save_to_json(self):
        os.makedirs(os.path.dirname(self.output_filename), exist_ok=True)
        json_output = json.dumps(self.unique_words, ensure_ascii=False)
        with open(self.output_filename, "w", encoding="utf-8") as f:
            f.write(json_output)
        return json_output

    def convert(self):
        self.load_and_process_excel()
        self.extract_unique_words()
        return self.save_to_json()


if __name__ == "__main__":
    converter = ExcelConverter(
        excel_filename="../resources/Szablon_HD_AI.xlsx",
        ignored_columns=["ID Zgłoszenia", "Data Zgłoszenia", "Produkt i wersja"],
    )
    converter.convert()
