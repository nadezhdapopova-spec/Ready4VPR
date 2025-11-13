from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig

from users.views import CustomUserViewSet


app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [

]

urlpatterns += router.urls
