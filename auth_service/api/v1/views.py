from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_service.api.v1.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)
from auth_service.authentication import generate_jwt_token


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "Пользователь успешно зарегистрирован.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        # token = generate_jwt_token(user.id)

        # return Response(
        #     {
        #         "message": "User registered successfully",
        #         "token": token,
        #         "user": {
        #             "id": user.id,
        #             "email": user.email,
        #             "first_name": user.first_name,
        #             "last_name": user.last_name,
        #             "role": "user",
        #         },
        #     },
        #     status=status.HTTP_201_CREATED,
        # )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = generate_jwt_token(user.id)
        return Response(
            {
                "access_token": token,
                "token_type": "Bearer",
                # "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


class MeView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "patronymic": user.patronymic,
                "role": user.role.name,
                "is_active": user.is_active,
            }
        )
