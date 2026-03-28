from django.urls import path
from . import views


app_name = 'arxivpapers'
urlpatterns = [
    # The homepage: displays papers and triggers auto-sync
    path('', views.paper_list_view, name='paper_list'),
    
    # The sync endpoint: triggered by the "Force Sync" button
    path('sync/', views.manual_sync_view, name='manual_sync'),
]
