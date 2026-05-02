
# Add this at the top of models.py
SPECIALIZATIONS = [
    ("Cardiologist", "Cardiologist"),
    ("Dermatologist", "Dermatologist"),
    ("Neurologist", "Neurologist"),
    ("Orthopedic", "Orthopedic"),
    ("Pediatrician", "Pediatrician"),
    ("Psychiatrist", "Psychiatrist"),
    ("General Physician", "General Physician"),
    ("ENT Specialist", "ENT Specialist"),
    ("Gastroenterologist", "Gastroenterologist"),
    ("Pulmonologist", "Pulmonologist"),
    ("Endocrinologist", "Endocrinologist"),
    ("Ophthalmologist", "Ophthalmologist"),
    ("Urologist", "Urologist"),
    ("Rheumatologist", "Rheumatologist"),
    ("Plastic Surgeon", "Plastic Surgeon"),
    ("Oncologist", "Oncologist"),
]

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import random

HOSPITALS = [
    "Apollo Hospital", "Fortis Hospital", "AIIMS", "Max Healthcare",
    "Narayana Health", "Manipal Hospital", "Medanta Hospital",
    "KIMS Hospital", "Columbia Asia Hospital", "Artemis Hospital"
]

class Doctor(models.Model):
    

    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATIONS)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    workplace = models.CharField(max_length=100, blank=True)
    working_hours = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if not self.workplace:
            self.workplace = random.choice(HOSPITALS)

        if not self.working_hours:
            self.working_hours = f"{random.randint(8, 12)} AM - {random.randint(3, 9)} PM"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.specialization} at {self.workplace}"

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Dr. {self.doctor.name} by {self.patient_name}"
    


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)  # 👈 ADD THIS
    appointment_date = models.DateField()
    time = models.TimeField()
    # Remove patient_name and patient_contact fields if you had them
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.name} on {self.appointment_date}"

class CounselingTest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TestQuestion(models.Model):
    test = models.ForeignKey(CounselingTest, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text


class TestAnswer(models.Model):
    question = models.ForeignKey(TestQuestion, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField()
    

    def __str__(self):
        return self.text


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(CounselingTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    result_text = models.TextField()
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.name} result"

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'


    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

# models.py

class MedicalRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='medical_records/')
    description = models.CharField(max_length=255, blank=True)  # <-- ADD THIS
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"
