# email_service.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from reports.models import GBVReport
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver

class GBVEmailService:
    """Service class for sending GBV system notifications"""
    
    @staticmethod
    def send_report_assigned_notification(report, professional, assigned_by=None):
        """Send notification when report is assigned to a professional"""
        
        context = {
            'report': report,
            'notification_title': 'Report Assignment Notification',
            'action_title': 'Your Report Has Been Assigned',
            'action_message': f'Your report has been assigned to {professional.get_full_name() or professional.username} ({professional.get_role_display()}) for review and action.',
            'action_button_url': f'{settings.FRONTEND_URL}/reports/{report.reference_code}',
            'action_button_text': 'View Report Status',
            'assigned_date': timezone.now(),
            'additional_info': f'Professional: {professional.get_full_name() or professional.username}\nRole: {professional.get_role_display()}',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=report,
            subject=f'Report #{report.reference_code} - Assigned for Review',
            context=context
        )
    
    @staticmethod
    def send_report_resolved_notification(report, resolution_notes=None):
        """Send notification when report is marked as resolved"""
        
        context = {
            'report': report,
            'notification_title': 'Report Resolution Notification',
            'action_title': 'Your Report Has Been Resolved',
            'action_message': 'We wanted to inform you that your report has been successfully resolved.',
            'action_button_url': f'{settings.FRONTEND_URL}/reports/{report.reference_code}',
            'action_button_text': 'View Resolution Details',
            'resolution_date': timezone.now(),
            'additional_info': resolution_notes if resolution_notes else 'No additional resolution notes provided.',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=report,
            subject=f'Report #{report.reference_code} - Resolved',
            context=context
        )
    
    @staticmethod
    def send_appointment_scheduled_notification(appointment):
        """Send notification when appointment is scheduled"""
        
        context = {
            'report': appointment.report,
            'notification_title': 'Appointment Scheduled',
            'action_title': 'Appointment Scheduled for Your Case',
            'action_message': f'An appointment has been scheduled for {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}.',
            'action_button_url': f'{settings.FRONTEND_URL}/appointments/{appointment.id}',
            'action_button_text': 'View Appointment Details',
            'appointment_date': appointment.appointment_date,
            'additional_info': f'Professional: {appointment.professional.get_full_name()}\nLocation: {appointment.location}\nType: {appointment.get_appointment_type_display()}' + (f'\n\nNotes: {appointment.notes}' if appointment.notes else ''),
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=appointment.report,
            subject=f'Appointment Scheduled - Report #{appointment.report.reference_code}',
            context=context
        )
    
    @staticmethod
    def send_appointment_status_update_notification(appointment, old_status):
        """Send notification when appointment status is updated"""
        
        status_messages = {
            'scheduled': 'Your appointment has been scheduled and confirmed.',
            'completed': 'Your appointment has been completed.',
            'cancelled': 'Your appointment has been cancelled.',
            'rescheduled': 'Your appointment has been rescheduled.',
        }
        
        context = {
            'report': appointment.report,
            'notification_title': 'Appointment Status Update',
            'action_title': f'Appointment {appointment.get_status_display()}',
            'action_message': status_messages.get(appointment.status, f'Your appointment status has been updated to {appointment.get_status_display()}.'),
            'action_button_url': f'{settings.FRONTEND_URL}/appointments/{appointment.id}',
            'action_button_text': 'View Appointment Details',
            'appointment_date': appointment.appointment_date,
            'additional_info': f'Professional: {appointment.professional.get_full_name()}\nStatus changed from {old_status} to {appointment.status}',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=appointment.report,
            subject=f'Appointment Update - Report #{appointment.report.reference_code}',
            context=context
        )
    
    @staticmethod
    def send_status_update_notification(report, old_status, updated_by, notes=None):
        """Send notification for general status updates"""
        
        status_messages = {
            'pending': 'Your report status has been updated to Pending and is awaiting review.',
            'under_review': 'Your report status has been updated to Under Review and is being actively investigated.',
            'resolved': 'Your report has been resolved.',
        }
        
        context = {
            'report': report,
            'notification_title': 'Report Status Update',
            'action_title': f'Status Updated: {report.get_status_display()}',
            'action_message': status_messages.get(report.status, f'Your report status has been updated to {report.get_status_display()}.'),
            'action_button_url': f'{settings.FRONTEND_URL}/reports/{report.reference_code}',
            'action_button_text': 'View Updated Report',
            'additional_info': notes if notes else f'Status updated by: {updated_by.get_full_name() or updated_by.username}\nChanged from {old_status} to {report.status}',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=report,
            subject=f'Status Update - Report #{report.reference_code}',
            context=context
        )
    
    @staticmethod
    def send_report_received_confirmation(report, password=None):
        """Send confirmation email when report is first submitted"""
        
        # If password is provided, include account creation info
        account_info = ""
        if password:
            account_info = f"\n\nYour account has been created:\nEmail: {report.reporter.email}\nPassword: {password}\n\nPlease change your password after logging in."
        
        context = {
            'report': report,
            'notification_title': 'Report Received Confirmation',
            'action_title': 'Your Report Has Been Received',
            'action_message': 'Thank you for submitting your report. We have received it and it will be reviewed by our team.' + account_info,
            'action_button_url': f'{settings.FRONTEND_URL}/reports/{report.reference_code}',
            'action_button_text': 'Track Your Report',
            'additional_info': 'You will receive updates as your report progresses through our system.',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=report,
            subject=f'Report Received - #{report.reference_code}',
            context=context
        )
    
    @staticmethod
    def send_case_note_added_notification(case_note):
        """Send notification when a new case note is added (only if not confidential)"""
        
        if case_note.is_confidential:
            return {'success': False, 'message': 'Confidential notes are not sent to reporters'}
        
        context = {
            'report': case_note.report,
            'notification_title': 'Case Update',
            'action_title': 'New Update Added to Your Case',
            'action_message': f'A new {case_note.get_note_type_display().lower()} note has been added to your case.',
            'action_button_url': f'{settings.FRONTEND_URL}/reports/{case_note.report.reference_code}',
            'action_button_text': 'View Case Updates',
            'additional_info': f'Note by: {case_note.created_by.get_full_name()}\nType: {case_note.get_note_type_display()}\n\n{case_note.content[:200]}{"..." if len(case_note.content) > 200 else ""}',
            'system_contact': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
        }
        
        return GBVEmailService._send_notification_email(
            report=case_note.report,
            subject=f'Case Update - Report #{case_note.report.reference_code}',
            context=context
        )
    
    @staticmethod
    def _send_notification_email(report, subject, context):
        """Internal method to send the actual email using EmailMultiAlternatives"""
        
        try:
            # Render the HTML template
            html_content = render_to_string('emails/gbv_notification.html', context)
            
            # Create plain text version by stripping HTML tags
            text_content = strip_tags(html_content)
            # Clean up the text content
            text_content = ' '.join(text_content.split())
            
            # Create the email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[report.reporter.email],
                bcc=[getattr(settings, 'ADMIN_EMAIL', None)] if hasattr(settings, 'ADMIN_EMAIL') and settings.ADMIN_EMAIL else []
            )
            
            # Attach the HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Send the email
            result = email.send()
            
            return {
                'success': result > 0,
                'message': 'Email sent successfully' if result > 0 else 'Failed to send email'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error sending email: {str(e)}'
            }

@receiver(post_save, sender=GBVReport)
def send_report_confirmation(sender, instance, created, **kwargs):
    """Send confirmation email when a new report is created"""
    if created:
        GBVEmailService.send_report_received_confirmation(instance)