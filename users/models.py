from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class City(models.Model):
    """Класс модели города (РФ)"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Город")

    def __str__(self):
        """Строковое отображение города"""
        return self.name


class CustomUser(AbstractUser):
    """Класс модели пользователя"""

    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = PhoneNumberField(
        region="RU", blank=True, null=True, verbose_name="Номер телефона", help_text="Необязательное поле"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        default="default/default.png",
        help_text="Необязательное поле",
    )
    city = models.ForeignKey(to=City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        """Строковое отображение пользователя"""
        return self.username or self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = [
            "email",
        ]


class Payment(models.Model):
    """Класс модели платежа"""

    METHOD_CHOICES = [
        ("STRIPE", "Stripe"),
    ]

    user = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Пользователь"
    )
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сумма платежа")
    paid_course = models.ForeignKey(
        to="lms.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course_payments",
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        to="lms.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lesson_payments",
        verbose_name="Оплаченный урок",
    )
    payment_method = models.CharField(max_length=8,
                                      choices=METHOD_CHOICES,
                                      verbose_name="Способ оплаты",
                                      default="STRIPE")
    status = models.CharField(max_length=50, default="unpaid")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")

    stripe_product_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID товара")
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID цены товара")
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии")
    stripe_payment_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на оплату")

    def clean(self):
        """Валидация: должен быть указан или курс, или урок"""
        if bool(self.paid_course) == bool(self.paid_lesson):
            raise ValidationError("Платеж должен ссылаться либо на курс, либо на урок")

    def __str__(self):
        """Строковое отображение платежа"""
        return f"Payment {self.id} - {self.payment_amount} ({self.status})"

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "платежи"
        ordering = ["-created_at"]
