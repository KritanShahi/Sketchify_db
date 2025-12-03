from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass  # built-in fields are enough

class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="uploads/")
    effect = models.CharField(max_length=50, default="sketch")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.effect} - {self.id}"
