from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели уроков"""

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели курсов"""

    lessons_count = serializers.SerializerMethodField(read_only=True)

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
        return instance.lesson_set.count()

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lessons_count", "lessons")
