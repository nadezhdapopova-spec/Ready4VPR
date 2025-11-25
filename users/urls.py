from django.urls import path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from users.apps import UsersConfig
from users.views import CustomUserViewSet, PaymentListViewSet, PaymentRetrieveViewSet


app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("payment/", PaymentListViewSet.as_view(), name="payment_list"),
    path("payment/<int:pk>/", PaymentRetrieveViewSet.as_view(), name="payment_detail"),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('token/verify/', TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns += router.urls
