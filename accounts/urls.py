from django.urls import path
from .views import signup, login, UploadImageView, UploadedImageListView,PublicImageListView,DeleteImageView,delete_public_image


urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("upload/", UploadImageView.as_view(), name="upload"),
    path('uploaded-images/', UploadedImageListView.as_view(), name='uploaded-images'),
    path("public-images/", PublicImageListView.as_view(), name="public-images"),
    path("delete-image/<int:id>/", DeleteImageView.as_view(), name="delete-image"),
    path('delete-public-image/<int:pk>/', delete_public_image, name='delete_public_image'),
]
