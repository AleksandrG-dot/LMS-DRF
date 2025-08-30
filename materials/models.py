from django.db import models


class Course(models.Model):
    """Модель с обучающими курсами"""
    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name="Название курса",
        help_text="Введите название курса",
    )
    preview = models.ImageField(
        upload_to="course/preview/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
        help_text="Загрузите превью",
    )
    description = models.TextField(
        verbose_name="Описание курса",
        help_text="Введите описание курса",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="Владелец",
        help_text="Укажите владельца",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """Модель с обучающими уроками"""
    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name="Название урока",
        help_text="Введите название урока",
    )
    description = models.TextField(
        verbose_name="Описание урока",
        help_text="Введите описание урока",
        blank=True,
        null=True,
    )
    preview = models.ImageField(
        upload_to="lesson/preview/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
        help_text="Загрузите превью",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Курс",
        help_text="Выберите курс",
    )
    link_video = models.URLField(blank=True, null=True)

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="Владелец",
        help_text="Укажите владельца",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
