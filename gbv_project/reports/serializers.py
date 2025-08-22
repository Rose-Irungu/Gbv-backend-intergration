from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import GBVReport
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

