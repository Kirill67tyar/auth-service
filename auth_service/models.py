from django.db import models

from auth_service.mixins import NameDescriptionMixin, TimeStampedMixin


class Role(NameDescriptionMixin, TimeStampedMixin):
    """Роли: admin, manager, user, guest и т.д."""

    class Meta:
        db_table = "roles"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class BusinessElement(NameDescriptionMixin, TimeStampedMixin):
    """Бизнес-объекты приложения: products, orders, access_rules и т.д."""

    class Meta:
        db_table = "business_elements"
        verbose_name = "Бизнес-элемент"
        verbose_name_plural = "Бизнес-элементы"

    def __str__(self):
        return self.name


class AccessRoleRule(TimeStampedMixin, models.Model):
    """Правила доступа: какая роль что может делать с каким элементом"""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name="rules")

    # Основные права
    read_permission = models.BooleanField(default=False, help_text="Может читать свои объекты")
    read_all_permission = models.BooleanField(default=False, help_text="Может читать ВСЕ объекты")

    create_permission = models.BooleanField(default=False)

    update_permission = models.BooleanField(
        default=False, help_text="Может редактировать свои объекты"
    )
    update_all_permission = models.BooleanField(
        default=False, help_text="Может редактировать ВСЕ объекты"
    )

    delete_permission = models.BooleanField(default=False, help_text="Может удалять свои объекты")
    delete_all_permission = models.BooleanField(
        default=False, help_text="Может удалять ВСЕ объекты"
    )

    class Meta:
        db_table = "access_role_rules"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "role",
                    "element",
                ],
                name="unique_key_role_element",
            )
        ]
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"

    def __str__(self):
        # return f"{self.role} -> {self.element}"
        return self.pk


class User(TimeStampedMixin, models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=255)

    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")

    is_active = models.BooleanField(default=True, help_text="False = мягкое удаление аккаунта")

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.pk} {self.email}"
