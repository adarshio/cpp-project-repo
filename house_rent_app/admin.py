from django.contrib import admin

# Register your models here.
from .models import UserProfile, House, Booking, Request

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'type', 'address', 'city')
    search_fields = ('user__username', 'phone_number', 'address', 'city')
    list_filter = ('type',)
    ordering = ('user',)    

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(House)
admin.site.register(Booking)
admin.site.register(Request)
