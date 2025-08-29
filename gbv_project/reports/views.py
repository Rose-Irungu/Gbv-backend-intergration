from reports.serializers import GBVReportSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from reports.permissions import IsAdminOrLawEnforcement
from rest_framework.decorators import action
from .models import GBVReport
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from rest_framework.decorators import action, permission_classes, api_view
from django.db.models import Q
from .serializers import (
    AppointmentSerializer, CaseNoteSerializer, 
    DocumentSerializer, CaseAssignmentSerializer
)
from .models import Appointment, CaseNote, Document, GBVReport, CaseAssignment

User = get_user_model()

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
        elif self.action in ["destroy", "list", "get_reporter", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return GBVReport.objects.all()
        elif user.role in ['doctor', 'lawyer', 'counselor']:
            assigned_reports = CaseAssignment.objects.filter(
                professional=user
            ).values_list('report', flat=True)
            return GBVReport.objects.filter(
                Q(pk__in=assigned_reports) | Q(appointments__professional=user)
            ).distinct()
        else:
            return GBVReport.objects.filter(reporter=user)
    
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

class BaseGBVViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_user_assigned_reports(self, user):
        if user.role == 'admin':
            return GBVReport.objects.all()
        elif user.role in ['doctor', 'lawyer', 'counselor']:
            assigned_reports = CaseAssignment.objects.filter(
                professional=user
            ).values_list('report', flat=True)
            return GBVReport.objects.filter(
                Q(pk__in=assigned_reports) | Q(appointments__professional=user)
            ).distinct()
        else:
            return GBVReport.objects.filter(reporter=user)

    def validate_report_access(self, report_id, user):
        try:
            report = GBVReport.objects.get(reference_code=report_id)
            
            if user.role == 'admin':
                return report
            elif user.role in ['doctor', 'lawyer', 'counselor']:
                assigned_to_case = CaseAssignment.objects.filter(
                    report=report, professional=user
                ).exists()
                has_appointment = report.appointments.filter(professional=user).exists()
                
                if assigned_to_case or has_appointment:
                    return report
                else:
                    raise serializers.ValidationError("You are not assigned to this case")
            elif report.reporter == user:
                return report
            else:
                raise serializers.ValidationError("Permission denied")
        except GBVReport.DoesNotExist:
            raise serializers.ValidationError("Report not found")

class AppointmentViewSet(BaseGBVViewSet):
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Appointment.objects.all()
        elif user.role in ['doctor', 'lawyer', 'counselor']:
            assigned_reports = CaseAssignment.objects.filter(
                professional=user
            ).values_list('report', flat=True)
            return Appointment.objects.filter(
                Q(professional=user) | Q(report__in=assigned_reports)
            )
        else:
            return Appointment.objects.filter(report__reporter=user)
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report')
        report = self.validate_report_access(report_id, self.request.user)
        serializer.save()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        
        if request.user.role == 'admin' or appointment.professional == request.user:
            new_status = request.data.get('status')
            if new_status in dict(Appointment.STATUS_CHOICES):
                appointment.status = new_status
                appointment.save()
                return Response(self.get_serializer(appointment).data)
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CaseNoteViewSet(BaseGBVViewSet):
    serializer_class = CaseNoteSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = CaseNote.objects.all()
        
        if user.role == 'admin':
            return queryset
        elif user.role in ['doctor', 'lawyer', 'counselor']:
            user_reports = self.get_user_assigned_reports(user)
            return queryset.filter(report__in=user_reports)
        else:
            return queryset.filter(report__reporter=user, is_confidential=False)
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report')
        report = self.validate_report_access(report_id, self.request.user)
        
        if self.request.user.role == 'survivor':
            serializer.save(created_by=self.request.user, note_type='general')
        else:
            serializer.save(created_by=self.request.user)

class DocumentViewSet(BaseGBVViewSet):
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Document.objects.all()
        elif user.role in ['doctor', 'lawyer', 'counselor']:
            user_reports = self.get_user_assigned_reports(user)
            return Document.objects.filter(report__in=user_reports)
        else:
            return Document.objects.filter(report__reporter=user)
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report')
        report = self.validate_report_access(report_id, self.request.user)
        serializer.save(uploaded_by=self.request.user)

class CaseAssignmentViewSet(ModelViewSet):
    serializer_class = CaseAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return CaseAssignment.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report')
        professional_id = self.request.data.get('professional')
        
        try:
            report = GBVReport.objects.get(reference_code=report_id)
            professional = User.objects.get(id=professional_id)
            
            if professional.role not in ['doctor', 'lawyer', 'counselor']:
                raise serializers.ValidationError("Can only assign to professionals")
            
            if CaseAssignment.objects.filter(
                report=report, professional=professional, is_active=True
            ).exists():
                raise serializers.ValidationError("Professional already assigned to this case")
            print("-----------------------------------------------------------")
            
            serializer.save(assigned_by=self.request.user)
            report.status = 'under_review'
            report.assigned_to = professional
            report.save()
            
        except GBVReport.DoesNotExist:
            raise serializers.ValidationError("Report not found")
        except User.DoesNotExist:
            raise serializers.ValidationError("Professional not found")
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['post'], url_path='assign/(?P<report_id>[^/.]+)/(?P<professional_id>[^/.]+)')
    def quick_assign(self, request, report_id=None, professional_id=None):
        try:
            report = GBVReport.objects.get(reference_code=report_id)
            professional = User.objects.get(id=professional_id)
            
            if professional.role not in ['doctor', 'lawyer', 'counselor']:
                return Response({'error': 'Can only assign professionals'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            assignment, created = CaseAssignment.objects.get_or_create(
                report=report,
                professional=professional,
                defaults={'assigned_by': request.user, 'is_active': True}
            )
            
            if not created and not assignment.is_active:
                assignment.is_active = True
                assignment.save()
                
            report.status = 'under_review'
            report.assigned_to = professional
            report.save()
            
            return Response(self.get_serializer(assignment).data)
            
        except GBVReport.DoesNotExist:
            return Response({'error': 'Report not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Professional not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'], url_path='unassign/(?P<report_id>[^/.]+)/(?P<professional_id>[^/.]+)')
    def quick_unassign(self, request, report_id=None, professional_id=None):
        try:
            assignment = CaseAssignment.objects.get(
                report__reference_code=report_id,
                professional_id=professional_id,
                is_active=True
            )
            assignment.is_active = False
            assignment.save()
            
            return Response({'message': 'Professional unassigned successfully'})
            
        except CaseAssignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def case_summary(request, report_id):
    try:
        report = GBVReport.objects.get(reference_code=report_id)
        user = request.user
        
        has_access = (
            user.role == 'admin' or 
            report.reporter == user or
            report.appointments.filter(professional=user).exists() or
            CaseAssignment.objects.filter(report=report, professional=user, is_active=True).exists()
        )
        
        if not has_access:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        appointments = Appointment.objects.filter(report=report)
        notes = CaseNote.objects.filter(report=report)
        documents = Document.objects.filter(report=report)
        assignments = CaseAssignment.objects.filter(report=report, is_active=True)
        
        if user.role == 'survivor':
            notes = notes.filter(is_confidential=False)
        
        data = {
            'report_reference': report.reference_code,
            'appointments': AppointmentSerializer(appointments, many=True).data,
            'notes': CaseNoteSerializer(notes, many=True).data,
            'documents': DocumentSerializer(documents, many=True).data,
            'assignments': CaseAssignmentSerializer(assignments, many=True).data,
        }
        
        return Response(data)
    
    except GBVReport.DoesNotExist:
        return Response({'error': 'Report not found'}, 
                    status=status.HTTP_404_NOT_FOUND)
        
class DashBoardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        dashboard_data = {}
        if request.user.role == 'admin':
            reports = GBVReport.objects.prefetch_related('assigned_reports').all()

            total_reports = reports.count()
            pending_reports = reports.filter(status="pending").count()
            under_review_reports = reports.filter(status="under_review").count()
            resolved_reports = reports.filter(status="resolved").count()
            urgent_cases = reports.filter(Q(status="pending") & Q(
                Q(immediate_danger=True) | Q(needs_medical_attention=True)
            )).order_by('-date_reported')[:5]
            assigned_reports = CaseAssignment.objects.filter().count()

            dashboard_data = {
                "total_reports": total_reports,
                "pending_reports": pending_reports,
                "under_review_reports": under_review_reports,
                "resolved_reports": resolved_reports,
                "assigned_reports": assigned_reports,
                "urgent_cases" : GBVReportSerializer(urgent_cases, many=True).data
            }
            
        if request.user.role == "survivor":
            reports = GBVReport.objects.filter(reporter=request.user)
            appointments = Appointment.objects.filter(report__reporter=request.user)
            
            dashboard_data = {
                "my_reports" : {
                    "total" : reports.count(),
                    "reports" : GBVReportSerializer(reports, many=True).data
                },
                "appoinntments" : AppointmentSerializer(appointments, many=True).data
            }

        return Response(dashboard_data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_proffesionals(request):
    professionals = User.objects.filter(
        role__in=['doctor', 'lawyer', 'counselor']
    ).values('id', 'first_name', 'last_name', 'email', 'role')
    
    return Response(professionals)