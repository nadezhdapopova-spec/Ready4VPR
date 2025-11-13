from rest_framework import viewsets

from users.models import CustomUser
from users.serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
