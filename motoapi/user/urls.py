"""
URL mappings for user API.
"""
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('token/', views.AuthTokenCreateView.as_view(), name='token'),
    path('profile/', views.ManagerUserView.as_view(), name='profile')
]
