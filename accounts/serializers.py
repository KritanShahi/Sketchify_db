from rest_framework import serializers
from .models import UploadedImage, User
from django.contrib.auth.password_validation import validate_password

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UploadedImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # for frontend URL
    image = serializers.ImageField(write_only=True)  # for saving
    username = serializers.CharField(source='user.username', read_only=True)  # <-- add this

    class Meta:
        model = UploadedImage
        fields = ("id", "image", "image_url", "effect","name", "created_at", "username")
        read_only_fields = ("created_at", "username")

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
