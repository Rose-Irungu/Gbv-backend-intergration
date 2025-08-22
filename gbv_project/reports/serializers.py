from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from reports.models import GBVReport, Appointment, CaseAssignment, CaseNote, Document
import string
import random

User = get_user_model()

class GBVReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GBVReport
        fields = '__all__'

    def create(self, validated_data):
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        email = validated_data.get('email')
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "password": password,
                "role": "survivor",
                "phone_number": validated_data.get("phone", ""),
                "first_name": validated_data.get("first_name", ""),
                "last_name": validated_data.get("last_name", "")
            }
        )

        if created:
            send_mail(
                subject="Your Account Has Been Created",
                message=f"""
Hello {user.first_name},

Your report has been received. An account has been created for you.

Login Details:
Email: {user.email}
Password: {password}

Please log in and update your password after your first login.

Regards,
Support Team
                """,
                from_email="roseirungu497@gmail.com",
                recipient_list=[user.email],
                fail_silently=False
            )

        report = GBVReport.objects.create(reporter=user, **validated_data)
        return report


class AppointmentSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.get_full_name', read_only=True)
    report_reference = serializers.CharField(source='report.reference_code', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CaseNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    report_reference = serializers.CharField(source='report.reference_code', read_only=True)
    
    class Meta:
        model = CaseNote
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    report_reference = serializers.CharField(source='report.reference_code', read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']


class CaseAssignmentSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.get_full_name', read_only=True)
    professional_role = serializers.CharField(source='professional.role', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    report_reference = serializers.CharField(source='report.reference_code', read_only=True)
    
    class Meta:
        model = CaseAssignment
        fields = '__all__'
        read_only_fields = ['assigned_by', 'assigned_date']