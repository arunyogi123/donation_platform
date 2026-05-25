from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from account.api.v1.serialziers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer
)

User = get_user_model()


# 🔐 REGISTER
class RegisterAPIView(APIView):

    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer,
        tags=["Auth"]
    )
    def post(self, request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "User registered successfully",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔑 LOGIN
class LoginAPIView(APIView):

    @extend_schema(
        request=LoginSerializer,
        tags=["Auth"]
    )
    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):

                return Response({
                    "message": "Login successful",
                    "user_id": user.id,
                    "email": user.email
                })

            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 👤 PROFILE
class ProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ProfileSerializer,
        tags=["Profile"]
    )
    def get(self, request):

        profile = getattr(request.user, "profile", None)

        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ProfileSerializer(profile).data)