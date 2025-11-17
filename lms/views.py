from rest_framework import generics, viewsets

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class BaseLessonAPIView(generics.GenericAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonList(BaseLessonAPIView, generics.ListAPIView):
    pass


class LessonRetrieve(BaseLessonAPIView, generics.RetrieveAPIView):
    pass


class LessonCreate(BaseLessonAPIView, generics.CreateAPIView):
    pass


class LessonUpdate(BaseLessonAPIView, generics.UpdateAPIView):
    pass


class LessonDelete(BaseLessonAPIView, generics.DestroyAPIView):
    pass
