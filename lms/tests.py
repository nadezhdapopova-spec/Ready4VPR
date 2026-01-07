from django.contrib.auth.models import Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from lms.models import Course, CourseSubscription, Lesson
from users.models import CustomUser


class TestBaseLMSViewSet(APITestCase):
    """Базовый клас для тестирования корректности работы CRUD приложения lms"""

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()
        self.superuser = CustomUser.objects.create_superuser(
            email="admin@test.com", username="admin", password="admin123"
        )
        self.user = CustomUser.objects.create_user(email="user@test.com", username="user", password="user123")
        self.moderator = CustomUser.objects.create_user(email="mod@test.com", username="mod", password="mod123")
        group = Group.objects.create(name="moderators")
        self.moderator.groups.add(group)

        self.stranger = CustomUser.objects.create_user(
            email="stranger@test.com", username="stranger", password="str123"
        )

        self.client_super = APIClient()
        self.client_super.force_authenticate(user=self.superuser)

        self.client_user = APIClient()
        self.client_user.force_authenticate(user=self.user)

        self.client_mod = APIClient()
        self.client_mod.force_authenticate(user=self.moderator)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)


class TestCourseViewSet(TestBaseLMSViewSet):
    """Тестирует корректность работы CRUD курсов"""

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()
        self.course = Course.objects.create(title="Test Course", owner=self.user)

    def test_list_courses_authenticated(self):
        """Проверяет, что отображается список курсов для авторизованных пользователей"""
        url = reverse("lms:courses-list")
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_courses_unauthenticated(self):
        """Проверяет, что не отображается список курсов для неавторизованных пользователей"""
        url = reverse("lms:courses-list")
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_course_unauthenticated(self):
        """Проверяет, что не отображается курс для неавторизованных пользователей"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_course_non_owner_and_non_moderator(self):
        """Проверяет, что авторизованный не автор и не модератор не может просматривать курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_stranger.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_course_owner(self):
        """Проверяет, что отображается курс для автора"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course_moderator(self):
        """Проверяет, что отображается курс для модератора"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_mod.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course_superuser(self):
        """Проверяет, что админ может создавать курс"""
        url = reverse("lms:courses-list")
        data = {"title": "New Course"}
        response = self.client_super.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Course.objects.filter(title="New Course").exists())

    def test_create_course_normal_user(self):
        """Проверяет, что авторизованный пользователь может создавать курс"""
        url = reverse("lms:courses-list")
        data = {"title": "User Course"}
        response = self.client_user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Course.objects.filter(title="User Course").exists())

    def test_create_course_moderator(self):
        """Проверяет, что модератор не может создавать курс"""
        url = reverse("lms:courses-list")
        data = {"title": "New Course"}
        response = self.client_mod.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course_owner(self):
        """Проверяет, что автор курса может редактировать курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        data = {"title": "Updated Course"}
        response = self.client_user.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Course")

    def test_update_course_moderator(self):
        """Проверяет, что модератор может редактировать курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        data = {"title": "Hacked Course"}
        response = self.client_mod.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_non_owner_and_non_moderator(self):
        """Проверяет, что пользователь не автор и не модератор не может редактировать курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        data = {"title": "Hacked by stranger"}
        response = self.client_stranger.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_owner(self):
        """Проверяет, что автор курса может удалить курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_delete_course_normal_user(self):
        """Проверяет, что авторизованный пользователь не автор курса не может удалить курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_stranger.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_moderator(self):
        """Проверяет, что модератор не может удалить курс"""
        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client_mod.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLessonViewSet(TestBaseLMSViewSet):
    """Тестирует корректность работы CRUD уроков"""

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()
        self.course = Course.objects.create(title="Test Course", owner=self.user)
        self.lesson = Lesson.objects.create(title="Test Lesson", owner=self.user)

    def test_list_lessons_authenticated(self):
        """Проверяет, что отображается список уроков для авторизованных пользователей"""
        url = reverse("lms:lesson_list")
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_lessons_unauthenticated(self):
        """Проверяет, что не отображается список уроков для неавторизованных пользователей"""
        url = reverse("lms:lesson_list")
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lesson_unauthenticated(self):
        """Проверяет, что не отображается урок для неавторизованных пользователей"""
        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lesson_non_owner_and_non_moderator(self):
        """Проверяет, что авторизованный не автор и не модератор не может просматривать урок"""
        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client_stranger.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_lesson_owner(self):
        """Проверяет, что отображается урок для автора"""
        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_moderator(self):
        """Проверяет, что отображается урок для модератора"""
        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client_mod.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson_superuser(self):
        """Проверяет, что админ может создавать урок"""
        url = reverse("lms:lesson_create")
        course_id = self.course.id
        data = {"title": "User Lesson", "category": course_id}
        response = self.client_super.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(title="User Lesson").exists())

    def test_create_lesson_normal_user_video_link(self):
        """Проверяет, что авторизованный пользователь может создавать урок с корректной ссылкой"""
        url = reverse("lms:lesson_create")
        course_id = self.course.id
        data = {
            "title": "User Lesson",
            "category": course_id,
            "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        response = self.client_user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(title="User Lesson").exists())

    def test_create_lesson_normal_user_bad_video_link(self):
        """Проверяет, что авторизованный пользователь не может создавать урок с некорректной ссылкой"""
        url = reverse("lms:lesson_create")
        course_id = self.course.id
        data = {"title": "User Lesson", "category": course_id, "video_link": "example.com"}
        response = self.client_user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lesson_moderator(self):
        """Проверяет, что модератор не может создавать урок"""
        url = reverse("lms:lesson_create")
        course_id = self.course.id
        data = {"title": "User Lesson", "category": course_id}
        response = self.client_mod.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_owner(self):
        """Проверяет, что автор курса может редактировать урок"""
        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"title": "Updated Lesson"}
        response = self.client_user.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Lesson")

    def test_update_lesson_moderator(self):
        """Проверяет, что модератор может редактировать урок"""
        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"title": "Hacked Lesson"}
        response = self.client_mod.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_non_owner_and_non_moderator(self):
        """Проверяет, что пользователь не автор и не модератор не может редактировать урок"""
        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"title": "Hacked by stranger"}
        response = self.client_stranger.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        """Проверяет, что автор курса может удалить урок"""
        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_lesson_normal_user(self):
        """Проверяет, что авторизованный пользователь не автор урока не может удалить урок"""
        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client_stranger.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_moderator(self):
        """Проверяет, что модератор не может удалить урок"""
        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client_mod.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCourseSubscriptionAPIView(APITestCase):
    """Тесты для подписки и отписки от курса"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="user@test.com", password="testpass123")
        self.client_user = APIClient()
        self.client_user.force_authenticate(self.user)

        self.course = Course.objects.create(title="Test Course", owner=self.user)

        self.url = reverse("lms:subscription")

    def test_subscription_requires_auth(self):
        """Проверяет, что неавторизованный пользователь не может отправлять запросы"""
        client = APIClient()
        response = client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_missing_course_id(self):
        """Если course_id не передан — ошибка 400"""
        response = self.client_user.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_add(self):
        """Проверяет, что когда подписки нет — она создаётся"""
        response = self.client_user.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_remove(self):
        """Проверяет, что когда подписка существует — она удаляется"""
        CourseSubscription.objects.create(user=self.user, course=self.course)

        response = self.client_user.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")

        self.assertFalse(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_toggle_behaviour(self):
        """Проверяет, что можно сначала добавить подписку, потом удалить"""
        first_add = self.client_user.post(self.url, {"course_id": self.course.id})
        self.assertEqual(first_add.status_code, status.HTTP_200_OK)

        self.assertTrue(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

        second_del = self.client_user.post(self.url, {"course_id": self.course.id})
        self.assertEqual(second_del.data["message"], "Подписка удалена")

        self.assertFalse(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())
