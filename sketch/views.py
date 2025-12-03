from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ImageHistory
from .serializers import HistorySerializer
from django.core.files.base import ContentFile
import base64

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_image(request):
    user = request.user
    image_file = request.FILES["image"]
    effect = request.POST.get("effect")

    # <-- Your AI processing happens here -->
    # For now we store original and processed same for structure demo

    processed = image_file

    # Save in database
    history = ImageHistory.objects.create(
        user=user,
        original_image=image_file,
        processed_image=processed,
        effect=effect
    )

    serializer = HistorySerializer(history)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    user = request.user
    images = ImageHistory.objects.filter(user=user).order_by("-created_at")

    serializer = HistorySerializer(images, many=True)
    return Response(serializer.data)
