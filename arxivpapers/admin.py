from django.contrib import admin
from .models import ArxivPaper

@admin.register(ArxivPaper)
class ArxivPaperAdmin(admin.ModelAdmin):
    list_display = ("arxiv_id","title")
    search_fields = ("arxiv_id","title")