from django.urls import path
from .views import RegisterAPIView,ProfileAPIView,LoginView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(),name="create-account"),
    path('profile/', ProfileAPIView.as_view(),name="check-profile"),
    path("login/", LoginView.as_view(),name="login-account"),
]