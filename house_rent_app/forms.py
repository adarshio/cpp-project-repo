from django import forms
from django.contrib.auth.models import User
from .models import UserProfile,House,Booking

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'type', 'address', 'city']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['title', 'description', 'rent', 'address', 'city', 'image', 'area', 'furnished', 'no_of_rooms']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'image': forms.ClearableFileInput(attrs={'multiple': False}),
        }

