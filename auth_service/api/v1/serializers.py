import bcrypt
from rest_framework import serializers

from auth_service.models import AccessRoleRule, BusinessElement, Role, User


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

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        email = validated_data.pop("email")

        # Хэшируем пароль через bcrypt
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        validated_data["password"] = hashed.decode("utf-8")
        validated_data["email"] = email.strip().lower()

        # По умолчанию даём роль 'user', если не указана
        try:
            user_role = Role.objects.get(name__iexact="user")
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


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "created",
            "modified",
        )
        read_only_fields = (
            "id",
            "created",
            "modified",
        )


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = (
            "id",
            "name",
            "description",
            "created",
            "modified",
        )
        read_only_fields = (
            "id",
            "created",
            "modified",
        )


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    element_name = serializers.CharField(source="element.name", read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = (
            "id",
            "role",
            "role_name",
            "element",
            "element_name",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
            "created",
            "modified",
        )
        read_only_fields = (
            "id",
            "created",
            "modified",
            "role_name",
            "element_name",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "role",
            "is_active",
        ]
        read_only_fields = ["id", "role", "is_active"]

    def validate_email(self, value):
        value = value.strip().lower()

        user = self.instance
        qs = User.objects.filter(email=value)
        if user is not None:
            qs = qs.exclude(pk=user.pk)

        if qs.exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        return value

    def update(self, instance, validated_data):
        if "email" in validated_data:
            validated_data["email"] = validated_data["email"].strip().lower()
        return super().update(instance, validated_data)


class SetRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    new_role_name = serializers.CharField()
