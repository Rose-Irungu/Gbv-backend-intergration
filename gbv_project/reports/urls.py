from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reports.views import ReportApiView

router = DefaultRouter()
router.register('reports', ReportApiView, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
