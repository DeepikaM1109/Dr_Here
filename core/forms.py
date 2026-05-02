from django import forms
from .models import Appointment, CounselingTest
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import TestAnswer
from .models import UserProfile, MedicalRecord

class TestAnswerForm(forms.ModelForm):
    class Meta:
        model = TestAnswer
        fields = ['text','score']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'time'] 

class CounselingTestForm(forms.ModelForm):
    class Meta:
        model = CounselingTest
        fields = '__all__'

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [ 'photo']

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['file', 'description']
# class ProfilePhotoForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['profile_photo']

# class MedicalRecordForm(forms.ModelForm):
#     class Meta:
#         model = MedicalRecord
#         fields = ['file']
