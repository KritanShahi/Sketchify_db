from django.urls import path
from .views import signup, login, UploadImageView, UploadedImageListView

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("upload/", UploadImageView.as_view(), name="upload"),
    path('uploaded-images/', UploadedImageListView.as_view(), name='uploaded-images'),
]
