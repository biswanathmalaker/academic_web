from django.urls import path
from . import views

app_name = 'literature'
urlpatterns = [
    path('', views.index, name='index'),

    # Books
    path('add-book/', views.add_book, name='add_book'),
    path('update-book/<int:pk>/', views.update_book, name='update_book'),
    path('delete-book/<int:pk>/', views.delete_book, name='delete_book'),

    # Chapters
    path('add-chapter/', views.add_chapter, name='add_chapter'),
    path('update-chapter/<int:pk>/', views.update_chapter, name='update_chapter'),
    path('delete-chapter/<int:pk>/', views.delete_chapter, name='delete_chapter'),

    # Sections
    path('add-section/', views.add_section, name='add_section'),
    path('update-section/<int:pk>/', views.update_section, name='update_section'),
    path('delete-section/<int:pk>/', views.delete_section, name='delete_section'),

    # Subsections
    path('add-subsection/', views.add_subsection, name='add_subsection'),
    path('update-subsection/<int:pk>/', views.update_subsection, name='update_subsection'),
    path('delete-subsection/<int:pk>/', views.delete_subsection, name='delete_subsection'),

    # SubSubsections
    path('add-subsubsection/', views.add_subsubsection, name='add_subsubsection'),
    path('update-subsubsection/<int:pk>/', views.update_subsubsection, name='update_subsubsection'),
    path('delete-subsubsection/<int:pk>/', views.delete_subsubsection, name='delete_subsubsection'),

    # Codes
    path('add-code/', views.add_code, name='add_code'),
    path('update-code/<int:pk>/', views.update_code, name='update_code'),
    path('delete-code/<int:pk>/', views.delete_code, name='delete_code'),
    path('view-codes/', views.view_codes, name='view_codes'),

    # Notes
    path('add-note/', views.add_note, name='add_note'),
    path('edit-note/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete-note/<int:pk>/', views.delete_note, name='delete_note'),
    path('upload-note-image/', views.upload_note_image, name='upload_note_image'),
    path('reorder-notes/', views.reorder_notes, name='reorder_notes'),

    # Reordering
    path('reorder-chapters/', views.reorder_chapters, name='reorder_chapters'),
    path('reorder-sections/', views.reorder_sections, name='reorder_sections'),
    path('reorder-subsections/', views.reorder_subsections, name='reorder_subsections'),
    path('reorder-subsubsections/', views.reorder_subsubsections, name='reorder_subsubsections'),
    path('reorder-books/', views.reorder_books, name='reorder_books'),
]