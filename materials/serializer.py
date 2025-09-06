from rest_framework import serializers

from users.models import Subscription
from .models import Course, Lesson
from .validators import validate_url_youtube


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели уроков"""

    link_video = serializers.URLField(validators=[validate_url_youtube], required=False)

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели курсов"""

    # Поле с количеством уроков у курса
    lessons_count = serializers.SerializerMethodField(read_only=True)

    # Поле с подпиской
    subscription = serializers.SerializerMethodField(read_only=True)

    # Первый вариант решения задачи 3: Вывод списка уроков для курса.
    # Вывод с помощью сериализатора для связанной модели
    lessons = LessonSerializer(source="lesson_set", many=True, read_only=True)

    # Второй вариант решения задачи 3: Вывод списка уроков для курса.
    # Через вычисляемые данные и списком
    # lessons = serializers.SerializerMethodField()
    #
    # def get_lessons(selfs, course):
    #     return [lesson.title for lesson in Lesson.objects.filter(course=course)]

    def get_lessons_count(self, instance):
        """Подсчитывает количество уроков в курса"""
        return instance.lesson_set.count()

    def get_subscription(self, obj):
        """Говорит есть ли подписка на обновления курса у текущего пользователя (из модели Subscription)"""
        user = self.context['request'].user # контекст автоматически передается при использовании ModelViewSet
        return Subscription.objects.filter(user=user, course=obj).exists()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "owner",
            "lessons_count",
            "subscription",
            "lessons",
        )
