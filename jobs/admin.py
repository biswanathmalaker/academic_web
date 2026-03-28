
from django.contrib import admin

from .models import PostdocPosition

@admin.register(PostdocPosition)

class PostdocPositionAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "job_url", "deadline")



