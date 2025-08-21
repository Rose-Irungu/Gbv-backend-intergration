from django.urls import path 
from accounts.views import AuthView
from .views import UserSignupView



urlpatterns = [
  path("", AuthView.as_view(), name="auth"),
  path('signup/', UserSignupView.as_view(), name='signup'),
  
  
]