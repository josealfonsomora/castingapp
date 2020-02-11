from rest_framework_simplejwt.serializers import TokenObtainSerializer
from django.contrib.auth.models import User


class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.username


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data
