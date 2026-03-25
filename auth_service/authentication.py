from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from auth_service.models import User


def generate_jwt_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "user_id": user_id,
        "exp": now + timedelta(hours=24),
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Токен просрочен") from None
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Неправильный токен") from None


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return None
        except ValueError:
            return None

        user_id = decode_jwt_token(token)
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed("Пользователь не найден") from None
