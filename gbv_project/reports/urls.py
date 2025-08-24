from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reports.views import (
    ReportApiView, CaseAssignmentViewSet, AppointmentViewSet,
    CaseNoteViewSet, DocumentViewSet, case_summary, DashboardView
)

router = DefaultRouter()
router.register('reports', ReportApiView, basename='reports')
router.register('assignments', CaseAssignmentViewSet, basename='assignment')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('notes', CaseNoteViewSet, basename='note')
router.register('documents', DocumentViewSet, basename='document')


urlpatterns = [
    path('', include(router.urls)),
    path('/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('cases/<str:report_id>/summary/', case_summary, name='case-summary'),
]
