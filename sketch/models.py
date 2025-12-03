from django.db import models
from django.contrib.auth.models import User

class ImageHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to="originals/")
    processed_image = models.ImageField(upload_to="results/")
    effect = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.effect}"
