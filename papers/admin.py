from django.contrib import admin
from .models import Paper , Statement , Topic, Category

@admin.register(Paper)

class PaperAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "year", "journal", "doi")
    search_fields = ("title", "authors", "doi", "key")
    list_filter = ("year", "journal")


# # admin.site.register(Section)
# # admin.site.register(Subsection)
@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
#     # search_fields = ('paper','section')
    list_display = ("text", "section", "paper" , "page_number")

#     # list_filter = ('paper','section')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
#     # search_fields = ('paper','section')
    list_display = ('name','description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}