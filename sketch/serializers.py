from rest_framework import serializers
from .models import ImageHistory

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageHistory
        fields = "__all__"
