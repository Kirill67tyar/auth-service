import bcrypt
from rest_framework import serializers

from auth_service.models import Role, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "password",
            "password2",
        ]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Хэшируем пароль через bcrypt
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        validated_data["password"] = hashed.decode("utf-8")

        # По умолчанию даём роль 'user', если не указана
        try:
            user_role = Role.objects.get(name="user")
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role": "lalala"}) from None
        return User.objects.create(
            **validated_data,
            role=user_role,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пароль или email неправильные.") from None

        if not bcrypt.checkpw(data["password"].encode("utf-8"), user.password.encode("utf-8")):
            raise serializers.ValidationError("Пароль или email неправильные.") from None

        data["user"] = user
        return data


class SetRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    new_role_name = serializers.CharField()
