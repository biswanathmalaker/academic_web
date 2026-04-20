from django.contrib import admin
from .models import Book , Chapter , Section , Subsection , SubSubsection , Code

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("book_name",)
    search_fields = ("book_name",)
    
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("chapter_name","book",)
    search_fields = ("chapter_name","book",)
    
# @admin.register(Section)
# class SectionAdmin(admin.ModelAdmin):
#     list_display = ("book_name",)
#     search_fields = ("book_name",)
    
# @admin.register(Subsection)
# class SubsectionAdmin(admin.ModelAdmin):
#     list_display = ("book_name",)
#     search_fields = ("book_name",)
    
# @admin.register(SubSubsection)
# class SubSubsectionAdmin(admin.ModelAdmin):
#     list_display = ("book_name",)
#     search_fields = ("book_name",)
    
# @admin.register(Code)
# class CodeAdmin(admin.ModelAdmin):
#     list_display = ("book_name",)
#     search_fields = ("book_name",)
