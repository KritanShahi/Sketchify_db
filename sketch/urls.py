from django.urls import path
from .views import process_image, get_history

urlpatterns = [
    path("process/", process_image),
    path("history/", get_history),
]
