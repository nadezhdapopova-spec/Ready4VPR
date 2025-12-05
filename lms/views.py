from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, CourseSubscription, Lesson
from lms.paginators import CoursePaginator, LessonPaginator
from lms.serializers import (
    CourseSerializer,
    CourseSubscriptionInputSerializer,
    CourseSubscriptionSerializer,
    LessonSerializer,
)
from users.permissions import IsModerator, IsOwner, NotModerator
from lms.tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    """Вьюсет курса"""

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = [
        "title",
    ]
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        """При создании курса устанавливает пользователя как владельца"""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """Определяет права на действия с курсами для разных уровней пользователей:
        - авторизованный суперпользователь - все права;
        - просмотр списка курсов - для авторизованных пользователей;
        - создание курсов - для авторизованных пользователей, но не модераторов;
        - просмотр и изменение курса - для авторизованных владельцев и модераторов;
        - удаление курса - для авторизованных владельцев
        """
        if self.request.user.is_superuser:
            return [IsAuthenticated()]
        if self.action == "list":
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [perm() for perm in self.permission_classes]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        previous_updated_at = instance.updated_at

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if timezone.now() - previous_updated_at >= timedelta(hours=4):
            send_course_update_email.delay(course_id=instance.id)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseLessonAPIView(generics.GenericAPIView):
    """Базовый вьюсет урока"""

    queryset = Lesson.objects.all().select_related("category")
    serializer_class = LessonSerializer


class LessonList(BaseLessonAPIView, generics.ListAPIView):
    """Вьюсет списка уроков"""

    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = ["category", "title"]
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator


class LessonRetrieve(BaseLessonAPIView, generics.RetrieveAPIView):
    """Вьюсет урока"""

    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonCreate(BaseLessonAPIView, generics.CreateAPIView):
    """Вьюсет создания урока"""

    permission_classes = [IsAuthenticated, NotModerator]

    def perform_create(self, serializer):
        """При создании урока устанавливает пользователя как владельца"""
        serializer.save(owner=self.request.user)


class LessonUpdate(BaseLessonAPIView, generics.UpdateAPIView):
    """Вьюсет редактирования урока"""

    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDelete(BaseLessonAPIView, generics.DestroyAPIView):
    """Вьюсет удаления урока"""

    permission_classes = [IsAuthenticated, IsOwner]


class CourseSubscriptionAPIView(APIView):
    """Вьюсет подписки пользователя на курс"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CourseSubscriptionInputSerializer,
        responses={
            200: CourseSubscriptionSerializer,
            400: "Ошибка запроса",
            404: "Курс не найден",
        },
    )
    def post(self, request):
        """
        Если подписки на курс нет - добавляет подписку,
        если подписка на курс есть - удаляет подписку
        """
        input_serializer = CourseSubscriptionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = request.user
        course_id = input_serializer.validated_data["course_id"]

        course = get_object_or_404(Course, id=course_id)
        subs = CourseSubscription.objects.filter(user=user, course=course).first()

        if subs:
            subs.delete()
            return Response({"message": "Подписка удалена"}, status=200)
        CourseSubscription.objects.create(user=user, course=course)
        output_serializer = CourseSubscriptionSerializer(subs)

        return Response(output_serializer.data, status=200)
