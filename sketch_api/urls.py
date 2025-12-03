from django.urls import path
from . import views

urlpatterns = [
    path('sketch/', views.sketch_api, name='sketch'),
]
