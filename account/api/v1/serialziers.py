from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Profile

User = get_user_model()


# 🔐 REGISTER
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data, password=password)

        # create profile automatically
        Profile.objects.create(user=user, full_name="", address="")

        return user


# 🔑 LOGIN
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# 👤 PROFILE
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["email", "full_name", "address", "created_at"]
