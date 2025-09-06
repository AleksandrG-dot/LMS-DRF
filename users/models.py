from django.contrib.auth.models import AbstractUser
from django.db import models

from config.settings import PAYMENT_METHOD
from materials.models import Course, Lesson


class User(AbstractUser):
    """Модель пользователя."""

    username = None
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите номер телефона",
    )
    city = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите Ваш город",
    )
    avatar = models.ImageField(
        upload_to="users/avatar",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"e-mail: {self.email}  city: {self.city}  phone: {self.phone}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    """Модель платежа."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    date = models.DateField(verbose_name="Дата оплаты", help_text="Введите дату оплаты")
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Курс",
        help_text="Выберите оплаченный курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.PROTECT,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Урок",
        help_text="Выберите оплаченный урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False,
        verbose_name="Сумма оплаты",
        help_text="Введите сумму оплаты",
    )
    payment_method = models.CharField(
        max_length=8,
        choices=PAYMENT_METHOD,
        default="transfer",
        blank=True,
        null=True,
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
    )

    def __str__(self):
        return f"Курс: {self.course if self.course else '-'} Урок: {self.lesson if self.lesson else '-'} Клиент: {self.user}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"


class Subscription(models.Model):
    """Модель подписок на обновления курсов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscription_users",
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course",
        blank=True,
        null=True,
        verbose_name="Курс",
        help_text="Выберите курс для подписки",
    )
