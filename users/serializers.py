from rest_framework import serializers

from users.models import CustomUser, Payment


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "city", "phone_number", "avatar")


class PaymentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "user", "payment_amount", "paid_course", "paid_lesson", "payment_method", "created_at")

