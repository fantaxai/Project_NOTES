from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ["me", "logout"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Регистрация нового пользователя"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserProfileSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def login(self, request):
        """Вход пользователя"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "Неверный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED
                )

            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "user": UserProfileSerializer(user).data,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                )

            return Response(
                {"error": "Неверный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Выход пользователя"""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Успешный выход"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Неверный токен"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получить профиль текущего пользователя"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
