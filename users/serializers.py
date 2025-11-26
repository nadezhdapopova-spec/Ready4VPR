from rest_framework import serializers

from users.models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели платежей"""
    paid_course = serializers.StringRelatedField()
    paid_lesson = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ("id", "user", "payment_amount", "paid_course", "paid_lesson", "payment_method", "created_at")


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного профиля пользователя"""
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "avatar", "city")


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для полного профиля пользователя"""
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "city", "phone_number", "avatar", "payments")


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "phone_number", "city", "avatar")

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            is_active=True,
        )
