from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name='papers'

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_paper, name="add_paper"),
    path("papers/<int:paper_id>/fetch_abstract/", views.fetch_abstract, name="fetch_abstract"),
    
    path('<int:paper_id>/manage_notes/', views.manage_notes, name='manage_notes'),
    path('<int:paper_id>/read_notes/', views.read_notes, name='read_notes'),

    path('add/', views.statement_create, name='statement_add'),
    path('update/<int:pk>/', views.statement_update, name='statement_update'),
    path('delete/<int:pk>/', views.statement_delete, name='statement_delete'),

    path("papers/<int:paper_id>/add_abstract/", views.add_abstract, name="add_abstract"),
    
    path('papers/all/', views.all_papers_detail, name='all_papers_detail'),
    path('papers/all/pdf/', views.all_papers_pdf, name='all_papers_pdf'),
    
    path("statements/", views.statement_list, name="statement_list"),
    path(
        "statements/by-topic/print/",
        views.statements_by_topic,
        name="statements_by_topic_print"
    ),
    path('papers/<int:paper_id>/update_categories/', views.update_categories, name='update_categories'),
]
