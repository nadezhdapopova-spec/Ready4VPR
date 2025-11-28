from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, CourseSubscription
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


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


class LessonRetrieve(BaseLessonAPIView, generics.RetrieveAPIView):
    """Вьюсет урока"""

    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonCreate(BaseLessonAPIView, generics.CreateAPIView):
    """Вьюсет создания урока"""

    permission_classes = [IsAuthenticated, ~IsModerator]

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

    def post(self, request):
        """
        Если подписки на курс нет - добавляет подписку,
        если подписка на курс есть - удаляет подписку
        """
        user = request.user
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"error": "Не указан course_id"}, status=400)

        course = get_object_or_404(Course, id=course_id)
        subs = CourseSubscription.objects.filter(user=user, course=course).first()

        if subs:
            subs.delete()
            message = "Подписка удалена"
        else:
            CourseSubscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message})
