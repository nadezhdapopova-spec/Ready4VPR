from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.models import CustomUser, Payment
from users.serializers import CustomUserSerializer, PaymentSerializer, RegisterSerializer


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny,]
    authentication_classes = []


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all().prefetch_related("payments")
    filter_backends = [OrderingFilter]
    ordering_fields = ("id",)


class PaymentListViewSet(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("created_at",)


class PaymentRetrieveViewSet(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
