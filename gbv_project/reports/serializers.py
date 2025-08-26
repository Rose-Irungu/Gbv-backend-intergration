from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from reports.models import GBVReport, Appointment, CaseAssignment, CaseNote, Document
import string
import random

User = get_user_model()

class GBVReportSerializer(serializers.ModelSerializer):
    # Read-only (for displaying reporter info)
    full_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    email = serializers.EmailField(source='reporter.email', read_only=True)
    phone = serializers.CharField(source='reporter.phone_number', read_only=True)

    # Write-only (for incoming requests)
    reporter_email = serializers.EmailField(write_only=True)
    reporter_first_name = serializers.CharField(write_only=True)
    reporter_last_name = serializers.CharField(write_only=True)
    reporter_phone = serializers.CharField(write_only=True)

    class Meta:
        model = GBVReport
        fields = '__all__'
        extra_kwargs = { 'reporter': {'required': False} }

    def create(self, validated_data):
        # Pull out the write-only fields
        user_email = validated_data.pop('reporter_email')
        first_name = validated_data.pop('reporter_first_name')
        last_name = validated_data.pop('reporter_last_name')
        phone = validated_data.pop('reporter_phone')

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                "role": "survivor",
                "phone_number": phone,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            send_mail(
                subject="Your Account Has Been Created",
                message=f"Hello {user.first_name},\n\nYour account has been created.\nEmail: {user.email}\nPassword: {password}",
                from_email="roseirungu497@gmail.com",
                recipient_list=[user.email],
            )

        return GBVReport.objects.create(reporter=user, **validated_data)


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