from rest_framework import serializers

from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели курсов"""

    lesson_count = serializers.SerializerMethodField(read_only=True)

    def get_lesson_count(self, instance):
        return instance.lesson_set.count()

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lesson_count")


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели уроков"""

    class Meta:
        model = Lesson
        fields = "__all__"
