from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_service.api.v1.serializers import LoginSerializer, RegisterSerializer
from auth_service.authentication import generate_jwt_token


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user.id)
            """
            import jwt
            encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
            jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            {'some': 'payload'}
            """

            return Response(
                {
                    "message": "User registered successfully",
                    "token": token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": "user",
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = generate_jwt_token(user.id)

            return Response(
                {
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.name,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

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
