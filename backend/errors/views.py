import os
import shutil
import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.excel_extractor import ExcelConverter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAVE_PATH = os.path.join(BASE_DIR, "resources/Szablon_HD_AI.xlsx")
BACKUP_DIR = os.path.join(BASE_DIR, "resources/backups")


def run_excel_converter():
    converter = ExcelConverter(
        excel_filename=SAVE_PATH,
        ignored_columns=["ID Zgłoszenia", "Data Zgłoszenia", "Produkt i wersja"],
    )
    converter.convert()


class ExcelUploadView(APIView):
    def post(self, request):
        try:
            file = request.FILES.get("excelFile")
            if not file:
                return Response({"error": "Plik nie został przesłany."}, status=400)

            os.makedirs(BACKUP_DIR, exist_ok=True)

            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"Szablon_HD_AI_{timestamp}.xlsx"
            backup_path = os.path.join(BACKUP_DIR, backup_name)

            with open(backup_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            shutil.copy2(backup_path, SAVE_PATH)

            with open(os.path.join(BACKUP_DIR, "active.txt"), "w") as f:
                f.write(backup_name)

            run_excel_converter()

            return Response(
                {"message": "Plik został poprawnie przesłany i zaktualizowany."},
                status=201,
            )

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)


class ListBackupsView(APIView):
    def get(self, request):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".xlsx")]
        backups.sort(reverse=True)

        active_file_path = os.path.join(BACKUP_DIR, "active.txt")
        active = None
        if os.path.exists(active_file_path):
            with open(active_file_path) as f:
                active = f.read().strip()

        return Response({"backups": backups, "active": active})


class SelectBackupView(APIView):
    def post(self, request):
        filename = request.data.get("filename")
        if not filename:
            return Response({"error": "Brak nazwy pliku."}, status=400)

        source_path = os.path.join(BACKUP_DIR, filename)

        if not os.path.exists(source_path):
            return Response({"error": "Plik nie istnieje."}, status=404)

        try:
            if os.path.exists(SAVE_PATH):
                os.remove(SAVE_PATH)
            shutil.copy2(source_path, SAVE_PATH)

            with open(os.path.join(BACKUP_DIR, "active.txt"), "w") as f:
                f.write(filename)

            run_excel_converter()

            return Response(
                {"message": "Plik został ustawiony jako aktywny i zaktualizowany."}
            )
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
