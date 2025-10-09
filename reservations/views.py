from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from reservations.models import Room, Reservation, Notification


def home(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, reservation__isnull=False).order_by('-created_at')
    else:
        notifications = []
    return render(request, 'home.html', {'notifications': notifications})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def available_rooms(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'available_rooms.html', {'rooms': rooms})

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

class LoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return '/admin-dashboard/'
        return '/'

def reserve_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            reservation_exists = Reservation.objects.filter(
                room=room,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()

            if reservation_exists:
                messages.error(request, f"{room.name} already reserved.")
            else:
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.room = room
                reservation.save()
                room.is_available = False
                room.save()

                Notification.objects.create(
                    user=request.user,
                    reservation=reservation,
                    message=f"{room.name} on {reservation.date} from {reservation.start_time} to {reservation.end_time} has been reserved.",
                )

                messages.success(request, f"{room.name} reserved.")
                return redirect('my_reservations')

    else:
        form = ReservationForm()

    return render(request, 'reserve_room.html', {'form': form, 'room': room})


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'my_reservations.html', {'reservations': reservations})

def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    Notification.objects.filter(reservation=reservation).delete()
    reservation.delete()
    messages.success(request, 'Reservation cancelled.')
    return redirect('my_reservations')

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            room = reservation.room
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            exist = Reservation.objects.filter(
                room=room,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=reservation.id).exists()

            if exist:
                messages.error(request, "This room is already reserved at that time.")
            else:
                form.save()
                messages.success(request, "Reservation updated successfully!")
                return redirect('my_reservations')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'edit_reservation.html', {'form': form, 'reservation': reservation})

def manage_users(request):
    users = User.objects.filter(is_staff=False, is_superuser=False)
    return render(request, 'manage_users.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('manage_users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:

        form = UserCreationForm()

    return render(request, 'add_user.html', {'form': form})

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields=['username', 'email']

@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False, is_superuser=False)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect('manage_user')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditUserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'user': user})

@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False, is_superuser=False)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('manage_users')
    return render(request, 'delete_user.html', {'user': user})

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description', 'is_available']

@user_passes_test(lambda u: u.is_staff)
def manage_rooms(request):
    rooms = Room.objects.all()
    return render(request, 'manage_rooms.html', {'rooms': rooms})


@user_passes_test(lambda u: u.is_staff)
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, "Room created successfully!")
            return redirect('manage_rooms')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm()

    return render(request, 'add_room.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully!")
            return redirect('manage_rooms')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm(instance=room)

    return render(request, 'edit_room.html', {'form': form, 'room': room})

@user_passes_test(lambda u: u.is_staff)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room deleted successfully!")
        return redirect('manage_rooms')
    return render(request, 'delete_room.html', {'room': room})

@user_passes_test(lambda u: u.is_staff)
def manage_reservations(request):
    reservations = Reservation.objects.select_related('room', 'user').order_by('-date', '-start_time')
    return render(request, 'manage_reservations.html', {'reservations': reservations})

class AdminReservationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False), label='Select User')
    room = forms.ModelChoiceField(queryset=Room.objects.filter(is_available=True), label='Select Room')
    class Meta:
        model = Reservation
        fields = ['user', 'room', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

@user_passes_test(lambda u: u.is_staff)
def admin_add_reservation(request):
    if request.method == 'POST':
        form = AdminReservationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            room = form.cleaned_data['room']
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            exist = Reservation.objects.filter(
                room=room,
                date=date,
                start_time=start_time,
                end_time=end_time
            ).exists()

            if exist:
                messages.error(request, f"{room.name} is reserved at that time.")
            else:
                form.save()
                messages.success(request, f"Reservation added for {user.username} in {room.name} successfully!")
                return redirect('manage_reservations')
    else:
        form = AdminReservationForm()
    return render(request, 'admin_add_reservation.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    Notification.objects.filter(reservation=reservation).delete()
    reservation.delete()
    messages.success(request, f"Reservation for {reservation.room.name} has been cancelled!")
    return redirect('manage_reservations')











