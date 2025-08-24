# auth_serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from reports.models import Appointment


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name" : user.get_full_name(),
                "user_type": user.role,
            }
        }

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
        

class UserSignupSerializer(serializers.ModelSerializer):
    appointments_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_active",
            "last_login",
            "date_joined", 
            "appointments_count",
            "reports_count",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def get_appointments_count(self, obj):
        if obj.role == 'survivor':
            count = Appointment.objects.filter(report__reporter=obj).count()
            if count:
                return count
            else:
                return 0
        else:
            return getattr(obj, "appointments_pro", []).count() if hasattr(obj, "appointments_pro") else 0

    def get_reports_count(self, obj):
        if obj.role == 'survivor':
            return getattr(obj, "survivor", []).count() if hasattr(obj, "survivor") else 0
        else:
            return getattr(obj, "lawyer", []).count() if hasattr(obj, "lawyer") else 0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["created_at"] = data.pop("date_joined", None)
        return data


    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data
        )
        if validated_data['role'] == 'admin':
            user.is_superuser = True
            user.is_staff = True
            user.save()
        return user      
