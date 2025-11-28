from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import CustomUser
from lms.models import Course


class TestCourseViewSet(APITestCase):
    """Тестирует корректность работы CRUD курсов"""

    def setUp(self):
        """Формирует тестовые данные"""
        super().setUp()
        self.superuser = CustomUser.objects.create_superuser(
            email="admin@test.com", username="admin", password="admin123"
        )
        self.user = CustomUser.objects.create_user(
            email="user@test.com", username="user", password="user123"
        )
        self.moderator = CustomUser.objects.create_user(
            email="mod@test.com", username="mod", password="mod123"
        )
        group = Group.objects.create(name="moderators")
        self.moderator.groups.add(group)

        self.stranger = CustomUser.objects.create_user(
            email="stranger@test.com", username="stranger", password="str123"
        )

        self.course = Course.objects.create(title="Test Course", owner=self.user)

        self.client_super = APIClient()
        self.client_super.force_authenticate(user=self.superuser)

        self.client_user = APIClient()
        self.client_user.force_authenticate(user=self.user)

        self.client_mod = APIClient()
        self.client_mod.force_authenticate(user=self.moderator)

        self.client_stranger = APIClient()
        self.client_stranger.force_authenticate(user=self.stranger)

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
        """Проверяет, что пользователь не автор и не модератор не может просматривать курс"""
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

    def tearDown(self):
        """Очищает тестовую базу данных"""
        Course.objects.all().delete()
        CustomUser.objects.all().delete()
