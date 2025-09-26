from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


@shared_task
def send_information_about_update(course_name, email_list):
    """Функция для отправки сообщения об обновлении."""
    subject = "Обновление курса"
    message = f"Курс {course_name}, на который вы подписаны был обновлен."
    from_email = EMAIL_HOST_USER
    send_mail(subject, message, from_email, email_list, fail_silently=False)
