from django.db import models
from datetime import datetime
from django.conf import settings
import string
import random

class ReportManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class GBVReport(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('physical', 'Physical Violence'),
        ('sexual', 'Sexual Violence'),
        ('emotional', 'Emotional/Psychological'),
        ('online', 'Online Bullying'),
        ('other', 'Other'),
    ]
    
    REPORT_STATUSES = (
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved')
    )
    
    # Personal Information (Required)
    name = models.CharField(max_length=255, help_text="Full name of the reporter")
    email = models.EmailField(help_text="Email address for contact")
    phone = models.CharField(max_length=20, help_text="Phone number for contact")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=REPORT_STATUSES, default="pending")
    incident_date = models.DateTimeField(default=datetime.now())
    incident_location = models.CharField(max_length=255, help_text="Location where the incident occurred") 
    incident_type = models.CharField(
        max_length=20, 
        choices=INCIDENT_TYPE_CHOICES, 
        default='physical',
        help_text="Type of incident reported"
    )
    description = models.TextField(help_text="Detailed description of the incident")
    is_deleted = models.BooleanField(default=False)
    # Safety Assessment
    immediate_danger = models.BooleanField(
        default=False, 
        help_text="Indicates if the reporter is in immediate danger"
    )
    needs_medical_attention = models.BooleanField(
        default=False, 
        help_text="Indicates if the reporter needs medical attention"
    )
    objects = ReportManager()
    # System Fields
    reference_code = models.CharField(
        max_length=50, 
        blank=True,
        primary_key=True,
        unique=True, 
        help_text="Unique reference code for tracking the report"
    )
    date_reported = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Generate reference code if not provided"""
        if not self.reference_code:
            self.reference_code = self.generate_reference_code()
        super().save(*args, **kwargs)
        
    def delete(self):
        self.is_deleted=True
        self.save()
    
    def generate_reference_code(self):
        """Generate a unique reference code"""
        while True:
            code = 'GBV' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not GBVReport.objects.filter(reference_code=code).exists():
                return code
    
    def __str__(self):
        return f"Report {self.reference_code} - {self.name} - {self.incident_location}"
    
    class Meta:
        ordering = ['-date_reported']
        verbose_name = "GBV Report"
        verbose_name_plural = "GBV Reports"