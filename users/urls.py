from django.urls import path

from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import CustomUserViewSet, PaymentListViewSet, PaymentRetrieveViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("payment/", PaymentListViewSet.as_view(), name="payment_list"),
    path("payment/<int:pk>/", PaymentRetrieveViewSet.as_view(), name="payment_detail"),
]

urlpatterns += router.urls
