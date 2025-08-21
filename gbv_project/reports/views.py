from reports.serializers import GBVReportSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import GBVReport


class ReportApiView(ModelViewSet):
    serializer_class = GBVReportSerializer
    queryset = GBVReport.objects.all()
    permission_classes = [AllowAny]
    