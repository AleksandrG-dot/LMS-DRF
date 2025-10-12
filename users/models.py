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
        return (f"Курс: {self.course if self.course else '-'} "
                f"Урок: {self.lesson if self.lesson else '-'} Клиент: {self.user}")

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


class PaymentCourseStripe(models.Model):
    """Модель оплаты курсов через экваиринг stripe.com"""
    # Ранее сделанную модель Payment не логично использовать, так как там есть способ оплаты за наличный расчет,
    # нет статуса (оплачено/не оплачено) и поддерживает оплату уроков (не только курсов).
    # Поэтому модель Payment считаю как модель с уже проведенными платежами, а PaymentCourseStripe содержащую
    # только платежи через Stripe. Как оплаченные (is_paid=True), так и не оплаченные (is_paid=False).
    # В случае оплаты (is_paid=True), переносить в модель Payment с флагом payment_method='transfer'.

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments_stripe",
        blank=True,
        null=False,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    date = models.DateField(verbose_name="Дата оплаты", auto_now_add=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="payments_stripe",
        blank=False,
        null=False,
        verbose_name="Курс",
        help_text="Выберите оплаченный курс",
    )
    amount = models.PositiveIntegerField(
        blank=True,
        null=False,
        verbose_name="Сумма оплаты",
        help_text="Укажите сумму оплаты",
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии",
        help_text="Укажите ID сессии",
    )
    link = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылку на оплату",
        help_text="Укажите ссылку на оплату",
    )
    is_paid = models.BooleanField(verbose_name="Статус оплаты", default=False)

    def __str__(self):
        return f"Курс: {self.course} Клиент: {self.user}"

    class Meta:
        verbose_name = "Платеж Stripe"
        verbose_name_plural = "Платежи Stripe"
