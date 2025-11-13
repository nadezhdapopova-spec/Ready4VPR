from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [

]

urlpatterns += router.urls
