from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from users.models import User


@shared_task
def send_information_about_update(course_name, email_list):
    """Функция для отправки сообщения об обновлении."""
    subject = "Обновление курса"
    message = f"Курс '{course_name}', на который вы подписаны, был обновлен."
    from_email = EMAIL_HOST_USER
    send_mail(subject, message, from_email, email_list, fail_silently=False)


@shared_task
def block_unused_user():
    """Функция блокировки пользователя не входившего в систему более одного месяца."""
    date_block = timezone.now() + relativedelta(months=-1)
    user_list = User.objects.filter(
        is_active=True, is_superuser=False, last_login__lt=date_block
    )
    for user in user_list:
        user.is_active = False
        user.save()
        print(user.email, user.is_active)
