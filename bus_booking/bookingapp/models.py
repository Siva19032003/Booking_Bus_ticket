from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Bus(models.Model):
    BUS_TYPE_CHOICES = [
        ('AC', 'AC'),
        ('Non-AC', 'Non-AC'),
    ]
    CLASS_TYPE_CHOICES = [
        ('Sleeper', 'Sleeper'),
        ('Seater', 'Seater'),
    ]

    bus_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    date = models.DateField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    bus_type = models.CharField(max_length=10, choices=BUS_TYPE_CHOICES, default='AC')
    bus_class = models.CharField(max_length=10, choices=CLASS_TYPE_CHOICES, default='Seater')
    pickup_point = models.CharField(max_length=100, default='Main Bus Stop')
    drop_point = models.CharField(max_length=100, default='Main Bus Stop')

    def __str__(self):
        return f"{self.bus_name} ({self.source} to {self.destination}) on {self.date}"


class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Seat {self.seat_number} - {'Booked' if self.is_booked else 'Available'}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    pickup = models.CharField(max_length=100, default='Unknown')
    drop = models.CharField(max_length=100, default='Unknown')
    seat_number = models.CharField(max_length=10)
    bus_type = models.CharField(max_length=20, choices=[('Seater', 'Seater'), ('Sleeper', 'Sleeper')], default='Seater')
    booking_date = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.passenger_name} booked {self.bus} on {self.date} from {self.pickup} to {self.drop}"
    