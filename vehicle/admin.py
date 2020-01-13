from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(Vehicle_Type)
admin.site.register(Vehicle)
admin.site.register(Booking)