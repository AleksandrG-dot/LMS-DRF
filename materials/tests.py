from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User


class LessonUserTestCase(APITestCase):
    """Тест-кейс для уроков с обычными пользователями."""

    def setUp(self):
        """Наполнение данными БД."""
        self.user = User.objects.create(
            email="user_1@skylearn.ru", phone="+7999888777", city="Владимир"
        )
        self.user2 = User.objects.create(email="user_2@skylearn.ru")
        self.course = Course.objects.create(
            title="Курс-тест 1", description="Курс в тесте", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1",
            description="Урок 1 в курс-тесте 1",
            course=self.course,
            link_video="youtube.co",
            owner=self.user,
        )
        self.lesson2 = Lesson.objects.create(
            title="Урок 2",
            description="Урок 2 без курса и без владельца",
            owner=self.user2,
        )
        self.client.force_authenticate(user=self.user)  # Аутентификации пользователя

    def test_lesson_retrieve(self):
        """Тестирование получения значений одного урока."""
        url = reverse("materials:lesson_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        # print(response.json())  # можно посмотреть что отвечает API
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)
        self.assertEqual(data.get("owner"), self.user.pk)

    def test_lesson_retrieve_error_permission(self):
        """Тестирование получения значений одного урока другого пользователя."""
        url = reverse("materials:lesson_retrieve", args=(self.lesson2.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            data.get("detail"), "You do not have permission to perform this action."
        )

    def test_lesson_create(self):
        """Тестирование создания урока с верной ссылкой."""
        url = reverse("materials:lesson_create")
        data = {"title": "Урок 2", "link_video": "http://youtube.com/yrok_2/see/"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 3)

    def test_lesson_create_error_link(self):
        """Тестирование создания урока с НЕ верной ссылкой."""
        url = reverse("materials:lesson_create")
        data = {"title": "Урок 3", "link_video": "http://vk.ru/yrok_2/see/"}
        response = self.client.post(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_json.get("link_video")[0],
            "Допустимы только ссылки на видео с youtube.com",
        )

    def test_lesson_create_error_link_2(self):
        """Тестирование создания урока с НЕ верным форматом ссылки."""
        url = reverse("materials:lesson_create")
        data = {"title": "Урок 3", "link_video": "youtube.com/yrok_2/see/"}
        response = self.client.post(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json.get("link_video")[0], "Enter a valid URL.")

    def test_lesson_update(self):
        """Тестирование изменения урока."""
        url = reverse("materials:lesson_update", args=(self.lesson.pk,))
        data = {
            "title": "Урок переименованный",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Урок переименованный")

    def test_lesson_update_error(self):
        """Тестирование изменения урока другого пользователя."""
        url = reverse("materials:lesson_update", args=(self.lesson2.pk,))
        data = {
            "title": "Урок переименованный",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            data.get("detail"), "You do not have permission to perform this action."
        )

    def test_lesson_delete(self):
        """Тестирование удаления урока."""
        # Сделал для того, что бы попробовать тестирование ViewSet'ов
        url = reverse("materials:lesson_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 1)

    def test_lesson_delete_error(self):
        """Тестирование удаления урока другого пользователя."""
        url = reverse("materials:lesson_delete", args=(self.lesson2.pk,))
        response = self.client.delete(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            data.get("detail"), "You do not have permission to perform this action."
        )

    def test_lesson_list(self):
        """Тестирование получения списка уроков."""
        # Должен быть только один урок. У второго урока владелец другой пользователь
        url = reverse("materials:lesson_list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "link_video": self.lesson.link_video,
                    "title": self.lesson.title,
                    "description": self.lesson.description,
                    "preview": self.lesson.preview,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class LessonModeratorTestCase(APITestCase):
    """Тест-кейс для уроков с пользователями-модераторами."""

    def setUp(self):
        """Наполнение данными БД."""
        self.user = User.objects.create(email="user_1@skylearn.ru")
        self.lesson = Lesson.objects.create(
            title="Урок 1 пользователя", owner=self.user
        )
        self.lesson2 = Lesson.objects.create(
            title="Урок 2 пользователя", owner=self.user
        )
        self.moder = User.objects.create(email="moderator@skylearn.ru")
        self.moder.groups.create(name="moders").save()
        self.client.force_authenticate(user=self.moder)

    def test_lesson_retrieve(self):
        """Тестирование получения значений одного урока пользователя."""
        url = reverse("materials:lesson_retrieve", args=(self.lesson2.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson2.title)
        self.assertEqual(data.get("owner"), self.user.pk)

    def test_lesson_create_error_permission(self):
        """Тестирование создания урока."""
        url = reverse("materials:lesson_create")
        data = {"title": "Урок 3", "link_video": "http://youtube.com/yrok_3/see/"}
        response = self.client.post(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response_json.get("detail"),
            "You do not have permission to perform this action.",
        )
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        """Тестирование изменения урока пользователя."""
        url = reverse("materials:lesson_update", args=(self.lesson.pk,))
        data = {
            "title": "Урок переименованный",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Урок переименованный")

    def test_lesson_delete_error(self):
        """Тестирование удаления урока пользователя."""
        url = reverse("materials:lesson_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            data.get("detail"), "You do not have permission to perform this action."
        )
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_list(self):
        """Тестирование получения списка уроков."""
        # Должны быть все два урока.
        url = reverse("materials:lesson_list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "link_video": self.lesson.link_video,
                    "title": self.lesson.title,
                    "description": self.lesson.description,
                    "preview": self.lesson.preview,
                    "course": None,
                    "owner": self.user.pk,
                },
                {
                    "id": self.lesson2.pk,
                    "link_video": self.lesson2.link_video,
                    "title": self.lesson2.title,
                    "description": self.lesson2.description,
                    "preview": self.lesson2.preview,
                    "course": None,
                    "owner": self.user.pk,
                },
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class LessonAnonymousUserTestCase(APITestCase):
    """Тест-кейс для уроков с неавторизованными пользователями."""

    def setUp(self):
        """Наполнение данными БД."""
        self.user = User.objects.create(email="user_1@skylearn.ru")
        self.lesson = Lesson.objects.create(
            title="Урок 1 пользователя", owner=self.user
        )
        self.lesson2 = Lesson.objects.create(
            title="Урок 2 пользователя", owner=self.user
        )

    def test_lesson_retrieve_error_permission(self):
        """Тестирование получения значений одного урока пользователя."""
        url = reverse("materials:lesson_retrieve", args=(self.lesson2.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            data.get("detail"), "Authentication credentials were not provided."
        )

    def test_lesson_create_error_permission(self):
        """Тестирование создания урока."""
        url = reverse("materials:lesson_create")
        data = {"title": "Урок 3", "link_video": "http://youtube.com/yrok_3/see/"}
        response = self.client.post(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response_json.get("detail"), "Authentication credentials were not provided."
        )
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update_error_permission(self):
        """Тестирование изменения урока пользователя."""
        url = reverse("materials:lesson_update", args=(self.lesson.pk,))
        data = {
            "title": "Урок переименованный",
        }
        response = self.client.patch(url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response_json.get("detail"), "Authentication credentials were not provided."
        )

    def test_lesson_delete_error_permission(self):
        """Тестирование удаления урока пользователя."""
        url = reverse("materials:lesson_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            data.get("detail"), "Authentication credentials were not provided."
        )
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_list_error_permission(self):
        """Тестирование получения списка уроков."""
        # Должны быть все два урока.
        url = reverse("materials:lesson_list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            data.get("detail"), "Authentication credentials were not provided."
        )


class CourseSubscriptionTestCase(APITestCase):
    """Тест-кейс для подписок на обновление курсов."""

    def setUp(self):
        self.user = User.objects.create(email="user@user.ru")
        self.course = Course.objects.create(title="Курс-тест 1", owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_course_subscription(self):
        url = reverse("users:subscription")
        data = {"course": "1"}
        request = self.client.post(url, data)  # Подписываемся
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.get("message"), "Подписка добавлена на курс 'Курс-тест 1'"
        )
        self.assertEqual(response.get("status"), True)

        url = reverse("materials:course-detail", args=(self.course.pk,))
        request = self.client.get(url)  # Получаем данные по курсу
        response = request.json()
        print(response)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("subscription"), True)

        url = reverse("users:subscription")
        data = {"course": "1"}
        request = self.client.post(url, data)  # Отписываемся
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.get("message"), "Подписка удалена на курс 'Курс-тест 1'"
        )
        self.assertEqual(response.get("status"), False)

        url = reverse("materials:course-detail", args=(self.course.pk,))
        request = self.client.get(url)  # Получаем данные по курсу
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("subscription"), False)


class CourseTestCase(APITestCase):
    """Тест-кейс для курсов."""

    # Сделал для того, что бы попробовать тестирование ViewSet'ов. НЕ ПОЛНЫЙ CRUD (нет list)!
    # По заданию 4 урока 32.1 делать не надо.

    def setUp(self):
        """Наполнение данными БД."""
        self.user = User.objects.create(
            email="user@skylearn.ru", phone="+7999888777", city="Владимир"
        )
        self.course = Course.objects.create(
            title="Курс-тест 1", description="Курс в тесте", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1",
            description="Урок 1 в курс-тесте 1",
            course=self.course,
            link_video="youtube.co",
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)  # Аутентификации пользователя

    def test_course_retrieve(self):
        """Тестирование получения значений одного курса."""
        # Сделал для того, что бы попробовать тестирование ViewSet'ов
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.course.title)
        self.assertEqual(data.get("lessons")[0].get("title"), self.lesson.title)

    def test_course_create(self):
        """Тестирование создания курса."""
        # Сделал для того, что бы попробовать тестирование ViewSet'ов
        url = reverse("materials:course-list")
        data = {
            "title": "Курс-тест 2",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_update(self):
        """Тестирование изменения курса."""
        # Сделал для того, что бы попробовать тестирование ViewSet'ов
        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {
            "title": "Курс-тест переименованный",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Курс-тест переименованный")

    def test_course_delete(self):
        """Тестирование удаления курса."""
        # Сделал для того, что бы попробовать тестирование ViewSet'ов
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)
