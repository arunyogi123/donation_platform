from django.urls import path
from .views import RegisterAPIView,ProfileAPIView,LoginView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('profile/', ProfileAPIView.as_view()),
    path("login/", LoginView.as_view()),
]