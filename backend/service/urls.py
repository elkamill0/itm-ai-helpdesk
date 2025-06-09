from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

from backend.api.views import AskViewSet, main_page
from backend.errors.views import ExcelUploadView, ListBackupsView, SelectBackupView

router = routers.DefaultRouter()
router.register(r"ask", AskViewSet, basename="ask")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", main_page),
    path("api/", include(router.urls)),
    path(
        "upload-excel/",
        lambda request: render(request, "upload_excel.html"),
        name="upload_excel",
    ),
    path(
        "api/errors/upload-excel/", ExcelUploadView.as_view(), name="api_upload_excel"
    ),
    path("api/errors/backups/", ListBackupsView.as_view(), name="api_list_backups"),
    path(
        "api/errors/select-backup/",
        SelectBackupView.as_view(),
        name="api_select_backup",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
