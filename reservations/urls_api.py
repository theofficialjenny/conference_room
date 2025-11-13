from django.urls import path, include
from rest_framework import routers
from .views_api import (
    RoomViewSet,
    ReservationViewSet,
    UserViewSet,
    NotificationViewSet,
    UserRegistrationView,
    LoginAPIView,
    CurrentUserView,
)

router = routers.DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
