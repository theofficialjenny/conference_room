"""
URL configuration for conference_reservation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from reservations import views
from reservations.views import home, LoginView, register, available_rooms, admin_dashboard
from reservations.views_api import UserRegistrationView, LoginAPIView

urlpatterns = [
path('admin/', admin.site.urls),
    path('users/', UserRegistrationView.as_view(), name='user-registration'),

path('api/', include('reservations.urls_api')),

    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('', home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register, name='register'),
    path('available-rooms/', available_rooms, name='available_rooms'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('reserve-room/<int:room_id>/', views.reserve_room, name='reserve_room'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('edit-reservation/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-rooms/', views.manage_rooms, name='manage_rooms'),
    path('add-room/', views.add_room, name='add_room'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('admin-add-reservation/', views.admin_add_reservation, name='admin_add_reservation'),
    path('admin-cancel-reservation/<int:reservation_id>/', views.admin_cancel_reservation, name='admin_cancel_reservation'),

]
