from django.urls import path
from rest_framework.routers import DefaultRouter

from lms.apps import LmsConfig
from lms.views import CourseViewSet, LessonList, LessonRetrieve, LessonCreate, LessonUpdate, LessonDelete


app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonList.as_view(), name="lesson_list"),
    path("lessons/<int:pk>/", LessonRetrieve.as_view(), name="lesson_detail"),
    path("lessons/create/", LessonCreate.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/update/", LessonUpdate.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", LessonDelete.as_view(), name="lesson_delete"),
]

urlpatterns += router.urls
