from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, UploadedImageSerializer
from .models import UploadedImage
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

# ---------- Signup ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Login ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
        }, status=200)

    return Response({"error": "Invalid credentials"}, status=400)



# ---------- Image Upload ----------
class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]  # <== IMPORTANT

    def post(self, request, *args, **kwargs):
        print("AUTH USER:", request.user)      # DEBUG
        print("IS AUTH:", request.user.is_authenticated)

        print("AUTH HEADER:", request.headers.get("Authorization"))

        serializer = UploadedImageSerializer(data=request.data)

        if serializer.is_valid():
            # Correct: assign the actual user instance
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadedImageListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]   # <-- explicitly optional
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        # Now DRF will automatically authenticate the user
        print("User in request:", self.request.user)
        return UploadedImage.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        return {"request": self.request}


# ---------- Public Images ----------
class PublicImageListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]  # Anyone can see
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        # Return all images, newest first
        return UploadedImage.objects.all().order_by('-created_at')

    def get_serializer_context(self):
        # Ensure image_url works correctly
        return {"request": self.request}


class DeleteImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        try:
            image = UploadedImage.objects.get(id=id)
        except UploadedImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only allow the owner to delete
        if image.user != request.user:
            return Response({"error": "You do not have permission to delete this image"}, status=status.HTTP_403_FORBIDDEN)

        image.delete()
        return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)


        # Admin-only delete
@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_public_image(request, pk):
    try:
        image = PublicImage.objects.get(pk=pk)
        image.delete()
        return Response({"detail": "Image deleted"}, status=status.HTTP_204_NO_CONTENT)
    except PublicImage.DoesNotExist:
        return Response({"detail": "Image not found"}, status=status.HTTP_404_NOT_FOUND)