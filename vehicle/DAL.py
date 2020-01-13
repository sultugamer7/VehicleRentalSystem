from django.contrib.auth.models import User
from .models import *
from django.db.models import Q

# Get username
def get_username(value):
    username = User.objects.filter(username=value)
    return username


# Get email
def get_email(value):
    email = User.objects.filter(email=value)
    return email


# Add User
def add_user(first_name, last_name, username, email, password):
    user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
    )
    user.save()
    return user


# Add user's extra data in client model
def add_client(user, birth):
    client = Client(user=user, birthdate=birth)
    client.save()


# Check if user is blacklisted
def is_blacklisted(user):
    client = Client.objects.get(user=user)
    return client.blacklisted


# Get user's birthdate
def get_birthdate(user):
    client = Client.objects.get(user=user)
    return client.birthdate


# Get bookings
def get_bookings():
    bookings = Booking.objects.all()
    return bookings


# Get user's bookings
def get_user_bookings(user):
    bookings = Booking.objects.all().filter(user=user).order_by("-from_date")
    return bookings


# Get available small town cars excluding vehicle in bookings
def get_small_vehicles(bookings):
    vehicles = Vehicle.objects.all().filter(
        Q(vehicle_type__vehicle_type="Small Town Car") &
        (~Q(id__in=[vehicle.vehicle.id for vehicle in bookings]))
    )
    return vehicles


# Get all available vehicles excluding vehicle in bookings
def get_vehicles(bookings):
    vehicles = Vehicle.objects.all().filter(
        ~Q(id__in=[vehicle.vehicle.id for vehicle in bookings]))
    return vehicles


# Get vehicle by brand and model
def get_vehicle(brand, model):
    vehicle = Vehicle.objects.get(brand=brand, model=model)
    return vehicle


# Add booking info
def book_vehicle(user, vehicle, from_date, from_time, to_date, to_time, cost):
    booking = Booking(
        user=user,
        vehicle=vehicle,
        from_date=from_date,
        from_time=from_time,
        to_date=to_date,
        to_time=to_time,
        cost=cost
    )
    booking.save()


# Get user's booking details
def get_booking_details(booking_id):
    bookings = Booking.objects.get(id=booking_id)
    return bookings


# Get vehicle bookings
def get_vehicle_booking(to_date, vehicle):
    booking = Booking.objects.get(from_date=to_date, vehicle=vehicle)
    return booking


# Extend vehicle return time
def extend_time(booking_id, time):
    booking = Booking.objects.get(id=booking_id)
    booking.to_time = time
    booking.save()


# Cancel booking
def cancel_booking(booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.delete()