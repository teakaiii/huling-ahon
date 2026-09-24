"""
URL configuration for Reports module.
"""
from django.urls import path
from .views import (
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    generate_report_view,
    report_statistics_view,
    export_report_view
)

urlpatterns = [
    path('', ReportListView.as_view(), name='report_list'),
    path('<uuid:report_id>/', ReportDetailView.as_view(), name='report_detail'),
    path('create/', ReportCreateView.as_view(), name='report_create'),
    path('generate/', generate_report_view, name='generate_report'),
    path('statistics/', report_statistics_view, name='report_statistics'),
    path('export/', export_report_view, name='export_report'),
]
