from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('success/', views.submission_success, name='submission_success'),
]
