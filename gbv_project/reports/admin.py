from django.contrib import admin
from .models import GBVReport, Appointment, CaseAssignment, CaseNote, Document

@admin.register(GBVReport)
class GBVReportAdmin(admin.ModelAdmin):
    list_display = [
        'reference_code', 
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
    search_fields = ['reference_code','incident_location']
    readonly_fields = ['reference_code', 'date_reported']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('reporter',)
        }),
        ('Incident Details', {
            'fields': ('incident_date', 'incident_location', 'incident_type', 'description', 'status')
        }),
        ('Safety Assessment', {
            'fields': ('immediate_danger', 'needs_medical_attention')
        }),
        ('System Information', {
            'fields': ('reference_code', 'date_reported'),
            'classes': ('collapse',)
        })
    )

admin.site.register(Appointment)
admin.site.register(CaseAssignment)
admin.site.register(CaseNote)
admin.site.register(Document)