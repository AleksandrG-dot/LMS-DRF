from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated

from config import settings
from users.models import Subscription
from users.permissions import IsModer, IsOwner

from .models import Course, Lesson
from .paginations import CustomPagination
from .serializer import CourseSerializer, LessonSerializer
from .task import send_information_about_update


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description="Вьюсет для отображения списка курсов"
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(operation_description="Вьюсет для создания курса"),
)
class CourseViewSet(viewsets.ModelViewSet):
    """Вьюсет для CRUD модели курсов."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        """Автоматическое сохранение авторизованного пользователя как владельца курса"""
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_permissions(self):
        """Расстановка прав доступа на запросы."""
        if self.action == "create":
            self.permission_classes = (IsAuthenticated, ~IsModer)
        elif self.action in ("update", "retrieve", "list"):
            self.permission_classes = (
                IsAuthenticated,
                IsModer | IsOwner,
            )
        elif self.action == "destroy":
            self.permission_classes = (IsAuthenticated, ~IsModer | IsOwner,)
        return super().get_permissions()

    def get_queryset(self):
        """Возвращает только курсы авторизованного пользователя."""
        if self.request.user.groups.filter(name="moders").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        sub_list = Subscription.objects.filter(course=course)
        email_list = [sub.user.email for sub in sub_list]

        # В тестовом режиме сообщение не отправляем (не запускаем celery и redis)
        if not settings.TEST_MODE:
            send_information_about_update.delay(course.title, email_list)


class LessonCreateApiView(CreateAPIView):
    """Дженерик для создания урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, ~IsModer,)

    def perform_create(self, serializer):
        """Автоматическое сохранение авторизованного пользователя как владельца урока"""
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonListApiView(ListAPIView):
    """Дженерик для отображения списков уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner,)
    pagination_class = CustomPagination

    def get_queryset(self):
        """Возвращает только уроки авторизованного пользователя."""
        if self.request.user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveApiView(RetrieveAPIView):
    """Дженерик для изменения урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)


class LessonUpdateApiView(UpdateAPIView):
    """Дженерик для обновления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)


class LessonDestroyApiView(DestroyAPIView):
    """Дженерик для удаления урока."""

    queryset = Lesson.objects.all()  # Можно не указывать queryset
    serializer_class = LessonSerializer
    permission_classes = (~IsModer | IsOwner,)
