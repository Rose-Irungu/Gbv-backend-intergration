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
        # Create GBV Report
        report = GBVReport.objects.create(**validated_data)

        # Check if user already exists
        email = validated_data.get('email')
        if not User.objects.filter(email=email).exists():
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Create user
            user = User.objects.create_user(
                # username=email,
                email=email,
                password=password,
                role='survivor',
                phone_number=validated_data.get('phone', ''),
                first_name=validated_data.get('name', '')
            )

            # Send credentials via email
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

        return report
