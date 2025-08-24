from django.urls import path 
from accounts.views import AuthView, UserSignupView, Users


urlpatterns = [
  path("", AuthView.as_view(), name="auth"),
  path('signup/', UserSignupView.as_view(), name='signup'),
  path('users/', Users.as_view(), name="users")
  
]