from __future__ import annotations

from django.db.models import QuerySet
from rest_framework.permissions import BasePermission

from auth_service.models import AccessRoleRule

ACTION_BY_METHOD = {
    "GET": "read",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}


def is_authenticated_user(user) -> bool:
    """
    Проверка на то, что пользователь действительно залогинен
    в рамках нашей собственной модели User.
    """
    return bool(user and getattr(user, "pk", None) and getattr(user, "is_active", False))


def is_admin_user(user) -> bool:
    """
    Проверка на роль администратора.
    """
    if not is_authenticated_user(user):
        return False

    role = getattr(user, "role", None)
    return bool(role and role.name.lower() == "admin")


def get_business_element_name(view) -> str | None:
    """
    Во view должен быть атрибут:
        business_element_name = "products"
    """
    return getattr(view, "business_element_name", None)


def get_access_rule(user, element_name: str) -> AccessRoleRule | None:
    """
    Берёт правило доступа для конкретной роли и элемента.
    """
    return (
        AccessRoleRule.objects.select_related("role", "element")
        .filter(role=user.role, element__name__iexact=element_name)
        .first()
    )


def is_owner(user, obj) -> bool:
    """
    Проверяет, является ли объект "своим".
    Ожидается поле owner_id у бизнес-объекта.
    """
    owner_id = getattr(obj, "owner_id", None)
    return owner_id == user.pk


def filter_queryset_by_rule(
    queryset: QuerySet,
    user,
    element_name: str,
) -> QuerySet:
    """
    Для list-эндпоинтов:
    - read_all_permission=True -> все объекты
    - read_permission=True -> только свои
    - иначе -> пусто
    """
    if not is_authenticated_user(user):
        return queryset.none()

    if is_admin_user(user):
        return queryset

    rule = get_access_rule(user, element_name)
    if rule is None:
        return queryset.none()

    if rule.read_all_permission:
        return queryset

    if rule.read_permission:
        return queryset.filter(owner_id=user.pk)

    return queryset.none()


class IsAdminRole(BasePermission):
    message = "Недостаточно прав. Требуется роль администратора."

    def has_permission(self, request, view):
        return is_admin_user(request.user)


class AccessPermission(BasePermission):
    """
    Универсальная проверка прав для ресурсов проекта.

    Во view нужно указать:
        business_element_name = "products"
    """

    message = "Недостаточно прав для выполнения этого действия."

    def has_permission(self, request, view):
        user = request.user
        element_name = get_business_element_name(view)

        if not is_authenticated_user(user):
            return False

        if is_admin_user(user):
            return True

        if not element_name:
            return False

        rule = get_access_rule(user, element_name)
        if rule is None:
            return False

        action = ACTION_BY_METHOD.get(request.method)
        if action is None:
            return False

        if action == "read":
            return rule.read_permission or rule.read_all_permission

        if action == "create":
            return rule.create_permission

        if action == "update":
            return rule.update_permission or rule.update_all_permission

        if action == "delete":
            return rule.delete_permission or rule.delete_all_permission

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not is_authenticated_user(user):
            return False

        if is_admin_user(user):
            return True

        element_name = get_business_element_name(view)
        if not element_name:
            return False

        rule = get_access_rule(user, element_name)
        if rule is None:
            return False

        action = ACTION_BY_METHOD.get(request.method)
        if action is None:
            return False

        if action == "read":
            if rule.read_all_permission:
                return True
            return rule.read_permission and is_owner(user, obj)

        if action == "update":
            if rule.update_all_permission:
                return True
            return rule.update_permission and is_owner(user, obj)

        if action == "delete":
            if rule.delete_all_permission:
                return True
            return rule.delete_permission and is_owner(user, obj)

        return False
