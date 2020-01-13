from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(blank=False)
    blacklisted = models.BooleanField(default=False, blank=False)
    # String representation of self
    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"


class Vehicle_Type(models.Model):
    vehicle_type = models.CharField(max_length=25, blank=False, unique=True)
    # String representation of self
    def __str__(self):
        return f"{self.pk} - {self.vehicle_type}"


class Vehicle(models.Model):
    brand = models.CharField(blank=False, max_length=25)
    model = models.CharField(blank=False, max_length=25)
    FUEL_CHOICES = (
        ('Hybrid', 'Hybrid'), ('Petrol', 'Petrol'), ('Diesel', 'Diesel')
    )
    fuel_type = models.CharField(blank=False, choices=FUEL_CHOICES, max_length=10)
    GEAR_CHOICES = (('Automatic', 'Automatic'), ('Manual', 'Manual'))
    gear_type = models.CharField(blank=False, choices=GEAR_CHOICES, max_length=10)
    hire_cost = models.DecimalField(max_digits=5, decimal_places=2)
    vehicle_type = models.ForeignKey(Vehicle_Type, null=True, on_delete=models.SET_NULL)
    image = models.FileField(upload_to="vehicles/", blank=False)
    description = models.TextField(blank=False)
    # String representation of self
    def __str__(self):
        return f"{self.pk} - {self.brand} {self.model} - £{self.hire_cost} / day"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING)
    from_date = models.DateField(blank=False)
    from_time = models.TimeField(blank=False)
    to_date = models.DateField(blank=False)
    to_time = models.TimeField(blank=False)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    # String representation of self
    def __str__(self):
        return f"{self.pk} - {self.user}  |  {self.vehicle.brand} {self.vehicle.model}  |  {self.from_date} - {self.to_date}  |  £{self.cost}"