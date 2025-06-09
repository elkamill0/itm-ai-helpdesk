import os
import traceback
import numpy as np
import pandas as pd
import uuid

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from utils.converter import enhancedOCR
from utils.correcter import TextCorrector
from model.sklearn.model import FAQPipeline
from metadata.metadata import FAQPipelineConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STOPWORDS_PATH = os.path.join(BASE_DIR, "resources/stopwords.json")
CORRECTIONS_PATH = os.path.join(BASE_DIR, "resources/output.json")

corrector = None
try:
    if os.path.exists(CORRECTIONS_PATH):
        reference_words = TextCorrector.load_reference_words_from_json(CORRECTIONS_PATH)
        corrector = TextCorrector(reference_words)
    else:
        print("[!] corrections.json not found.")
except Exception as e:
    traceback.print_exc()
    print(f"[ERROR] Failed to load corrections: {e}")


def serialize(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (pd.Timestamp, pd.NaT.__class__)):
        return str(obj) if pd.notnull(obj) else None
    elif pd.isna(obj):
        return None
    return obj


def main_page(request):
    return render(request, "index.html")


class AskViewSet(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request):
        print(">>> [create] Request received")

        selected_columns = request.data.getlist("columns")
        if not selected_columns:
            selected_columns = ["Opis Błędu", "Załączniki"]
        print(">>> [create] Wybrane kolumny:", selected_columns)

        config = FAQPipelineConfig(
            file_path=os.path.join(BASE_DIR, "resources/Szablon_HD_AI.xlsx"),
            col_names=selected_columns,
            stopwords_path=STOPWORDS_PATH,
        )
        faq_model = FAQPipeline(config)

        check_typos = request.data.get("check_typos", "true").lower() == "true"
        print(">>> [create] Sprawdzanie literówek:", check_typos)

        min_similarity_str = request.data.get("min_similarity", "40")
        try:
            min_similarity = float(min_similarity_str)
        except ValueError:
            min_similarity = 40.0
        print(">>> [create] Minimalne podobieństwo (procent):", min_similarity)

        user_input = request.data.get("prompt", "").strip()
        corrected_prompt = (
            corrector.correct_text(user_input)
            if check_typos and corrector
            else user_input
        )
        print(">>> [create] Corrected prompt:", corrected_prompt)

        image_file = request.FILES.get("image")
        extracted_text = ""

        if image_file:
            try:
                print(">>> [create] Image received. Processing...")
                safe_filename = f"{uuid.uuid4().hex}.png"
                temp_path = default_storage.save(
                    "temp/" + safe_filename, ContentFile(image_file.read())
                )
                image_path = default_storage.path(temp_path)

                enc_ocr = enhancedOCR(image_path)
                raw_text = enc_ocr.convert_to_text()
                print(">>> [create] Raw extracted text:", raw_text)

                extracted_text = (
                    corrector.correct_text(raw_text)
                    if check_typos and corrector
                    else raw_text
                )
                print(">>> [create] Corrected extracted text:", extracted_text)

                default_storage.delete(temp_path)
            except Exception as e:
                traceback.print_exc()
                return Response(
                    {"error": f"Error processing image: {str(e)}"}, status=400
                )

        combined_text = corrected_prompt
        if extracted_text:
            combined_text += "\n" + extracted_text

        if not combined_text:
            return Response({"error": "Brak treści."}, status=400)

        try:
            print(">>> [create] Sending to FAQ model...")
            print(">>> Full input:\n", combined_text)

            all_answers = faq_model.find_top_answers(
                combined_text, similarity_metric="combined", top_n=10
            )

            filtered = [row for row in all_answers if row[-1] >= min_similarity]

            print(">>> [create] Top odpowiedzi (po filtrze):")
            for i, row in enumerate(filtered):
                print(f"--- Odpowiedź #{i + 1} ---")
                for j, val in enumerate(row):
                    if isinstance(val, (np.integer, np.int64)):
                        val = int(val)
                    elif isinstance(val, (np.floating, np.float64)):
                        val = f"{float(val):.2f}%"
                    elif isinstance(val, (pd.Timestamp, pd.NaT.__class__)):
                        val = str(val) if pd.notnull(val) else "NaT"
                    elif pd.isna(val):
                        val = "NULL"
                    print(f"  [{j}] {val}")

            serialized_answers = [[serialize(v) for v in row] for row in filtered]
            return Response({"answers": serialized_answers})
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
