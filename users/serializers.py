from rest_framework import serializers

from users.models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    paid_course = serializers.StringRelatedField()
    paid_lesson = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ("id", "user", "payment_amount", "paid_course", "paid_lesson", "payment_method", "created_at")


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "city", "phone_number", "avatar", "payments")


class RegisterSerializer(serializers.ModelSerializer):
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
