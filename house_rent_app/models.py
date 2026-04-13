from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    type = models.BooleanField(default=False)  # True for owner, False for tenant
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class House(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    rent = models.IntegerField()
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='house_images/')
    created_at = models.DateTimeField(default=timezone.now)
    area = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='houses')
    is_available = models.BooleanField(default=True)
    furnished = models.BooleanField(default=False)
    no_of_rooms = models.IntegerField(default=1)

    def __str__(self):
        return self.title



class Booking(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tenant.username} booked {self.house.title}"


class Request(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='requests')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)  

    def __str__(self):
        return f"Request from {self.tenant.username} for {self.house.title}"