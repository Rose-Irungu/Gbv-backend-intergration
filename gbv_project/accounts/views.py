# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSignupSerializer
from .models import User


from .serializers import (
    LoginSerializer,
    ChangePasswordSerializer,
    ResetPasswordRequestSerializer,
    ProfileUpdateSerializer,
)

User = get_user_model()

class AuthView(APIView):
    def get_permissions(self):
        if self.request.method == "POST" and self.request.query_params.get("action") == "login":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if request.query_params.get("user_id") and user.role == "admin":
            try:
                user = User.objects.get(id=request.query_params.get("user_id"))
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=404)
        serializer = UserSignupSerializer(user)
        return Response({
            "result_code": 0,
            "message": "User details fetched successfully",
            "data": serializer.data
        })

    def post(self, request, *args, **kwargs):
        action = request.query_params.get("action")
        
        if action == "login":
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response({
                "result_code": 0,
                "message": "Login successful",
                "data": serializer.validated_data
            })

        elif action == "reset_password":
            serializer = ResetPasswordRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                temp_password = get_random_string(8)
                user.set_password(temp_password)
                user.save()

                send_mail(
                    "Your Temporary Password",
                    f"Your new password is: {temp_password}\nPlease change it after logging in.",
                    "noreply@yourapp.com",
                    [email],
                    fail_silently=False
                )
                return Response({"detail": "Password reset. Check your email."})
            except User.DoesNotExist:
                return Response({"detail": "Email not found."}, status=404)

        return Response({"detail": "Invalid action"}, status=400)

    def put(self, request, *args, **kwargs):
        action = request.query_params.get("action")

        if action == "change_password":
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"detail": "Old password incorrect"}, status=400)

            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"detail": "Password changed successfully."})

        elif action == "update_profile":
            serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "Profile updated", "user": serializer.data})

        return Response({"detail": "Invalid action"}, status=400)# accounts/views.py


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        role = response.data['role']
        return Response({
            'result_code': 0,
            'message': 'User created successfully',
            'role': role
        }, status=status.HTTP_201_CREATED)

class Users(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSignupSerializer(users, many=True)
        return Response({
            "result_code": 0,
            "message" : "User retrieved successfully",
            "data" : serializer.data
        })
  
  
