from django.contrib import admin

from core.upload.models import UploadFile, UploadLink

admin.site.register(UploadLink)
admin.site.register(UploadFile)
