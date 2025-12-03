from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lms.models import Course, Lesson
from users.models import CustomUser, Payment
from users.permissions import IsProfileOwner, IsOwner, IsModerator
from users.serializers import CustomUserSerializer, PaymentSerializer, PublicUserSerializer, RegisterSerializer, \
    PaymentCreateSerializer
from users.services import create_stripe_product, create_stripe_price, create_checkout_session


class RegisterAPIView(CreateAPIView):
    """Представление для регистрации пользователя"""

    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []


class CustomUserViewSet(viewsets.ModelViewSet):
    """Представление для модели пользователя"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all().prefetch_related("payments")
    filter_backends = [OrderingFilter]
    ordering_fields = ("id",)
    permission_classes = [IsAuthenticated,]

    def get_serializer_class(self):
        """
        Возвращает публичный или полный сериализатор в зависимости от прав пользователя:
        если пользователь владелец - полный сериализатор, если нет - публичный
        """

        if self.action == "retrieve":
            user = self.get_object()
            if user.id != self.request.user.id:
                return PublicUserSerializer
            return CustomUserSerializer

        if self.action in ["update", "partial_update"]:
            return CustomUserSerializer

        if self.action == "list":
            return PublicUserSerializer

        return CustomUserSerializer

    def get_permissions(self):
        """
        Определяет права владельца профиля на изменение и удаление своего профиля, если владелец авторизован.
        Остальные действия доступны для авторизованных пользователей
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProfileOwner()]
        return [IsAuthenticated()]


class PaymentListViewSet(generics.ListAPIView):
    """Представление для просмотра платежей"""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("created_at",)
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        """
        Все платежи может просматривать админ и модератор,
        авторизованный пользователь видит свои платежи
        """

        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class PaymentRetrieveViewSet(generics.RetrieveAPIView):
    """Представление для просмотра деталей платежа"""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated,]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return obj
        if obj.user != user:
            raise PermissionDenied("Вы не можете просматривать чужой платеж")
        return obj


class PaymentCreateViewSet(generics.CreateAPIView):
    """Представление для создания платежа через API STRIPE"""

    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        """Создает платеж, возвращает данные платежа с ссылкой для оплаты"""
        user = self.request.user
        course_id = serializer.validated_data.get("course_id")
        lesson_id = serializer.validated_data.get("lesson_id")

        if course_id:
            course = get_object_or_404(Course, id=course_id)
            amount = course.price
            payment = Payment.objects.create(
                user=user, paid_course=course, payment_amount=amount
            )
            product_name = f"Оплата курса: {course.title}"
        else:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            amount = lesson.price
            payment = Payment.objects.create(
                user=user, paid_lesson=lesson, payment_amount=amount
            )
            product_name = f"Оплата урока: {lesson.title}"

        product_id = create_stripe_product(product_name)
        payment.stripe_product_id = product_id

        price_id = create_stripe_price(product_id, int(amount * 100))
        payment.stripe_price_id = price_id

        session_id, payment_url = create_checkout_session(price_id, payment.id)
        payment.stripe_session_id = session_id
        payment.stripe_payment_url = payment_url

        payment.save()

        self.response_data = {
            "payment_id": payment.id,
            "checkout_url": payment_url,
            "payment_amount": payment.payment_amount
        }

    def create(self, request, *args, **kwargs):
        """Переопределяет базовый метод create, чтобы вернуть кастомный Response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.response_data, status=201)
