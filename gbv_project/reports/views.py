from reports.serializers import GBVReportSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from reports.permissions import IsAdminOrLawEnforcement
from rest_framework.decorators import action
from .models import GBVReport


class ReportApiView(ModelViewSet):
    serializer_class = GBVReportSerializer
    queryset = GBVReport.objects.all()
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        Customize permissions per action.
        """
        if self.action in ["update", "partial_update"]:
            return [IsAdminOrLawEnforcement()]
        elif self.action in ["destroy", "list"]:
            return [IsAdminUser()]
        elif self.action in ["get_reporter", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='get_reports')
    def get_reporter(self, request):
        """
        Returns all reports submitted by the currently logged-in user.
        """
        if request.user.role == "survivor":
            reports = self.get_queryset().filter(reporter=request.user)
        elif request.user.role == "lawyer":
            reports = self.get_queryset().filter(assigned_to=request.user)
        else:
            reports = self.get_queryset().none()
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    