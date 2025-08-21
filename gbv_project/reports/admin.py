from django.contrib import admin
from .models import GBVReport

@admin.register(GBVReport)
class GBVReportAdmin(admin.ModelAdmin):
    list_display = [
        'reference_code', 
        'name', 
        'incident_type', 
        'incident_location', 
        'immediate_danger',
        'needs_medical_attention',
        'date_reported'
    ]
    list_filter = [
        'incident_type', 
        'immediate_danger', 
        'needs_medical_attention',
        'date_reported'
    ]
    search_fields = ['reference_code', 'name', 'email', 'incident_location']
    readonly_fields = ['reference_code', 'date_reported']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Incident Details', {
            'fields': ('incident_date', 'incident_location', 'incident_type', 'description')
        }),
        ('Safety Assessment', {
            'fields': ('immediate_danger', 'needs_medical_attention')
        }),
        ('System Information', {
            'fields': ('reference_code', 'date_reported'),
            'classes': ('collapse',)
        })
    )
