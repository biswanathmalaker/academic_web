from django.urls import path
from . import views
from .views import PositionCreateView, PositionListView


app_name = "jobs"

urlpatterns = [
    path("", views.DashboardView, name="dashboard"),
    path('positions/', PositionListView.as_view(), name='position_list'),
    path('positions/add/', PositionCreateView.as_view(), name='position_add'),

#     path("applications/", views.ApplicationListView.as_view(),
#          name="application_list"),

#     path("applications/add/", views.ApplicationCreateView.as_view(),
#          name="application_add"),

#     path("applications/<int:pk>/",
#          views.ApplicationDetailView.as_view(),
#          name="application_detail"),

#     path("applications/<int:pk>/edit/",
#          views.ApplicationUpdateView.as_view(),
#          name="application_edit"),

#     path("applications/<int:pk>/delete/",
#          views.ApplicationDeleteView.as_view(),
#          name="application_delete"),

#     path("applications/<int:application_id>/communication/add/",
#          views.add_communication,
#          name="add_communication"),
#     path(
#         "job-ads/",
#         views.JobAdvertisementListView.as_view(),
#         name="job_advertisement_list",
#     ),
]
