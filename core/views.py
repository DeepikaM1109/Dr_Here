from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from .models import Doctor, Appointment, CounselingTest, MedicalRecord,UserProfile

from .forms import UserRegisterForm, AppointmentForm, UserUpdateForm, UserProfileForm, MedicalRecordForm
from django.contrib import messages
from django.http import JsonResponse
from geopy.distance import geodesic
from math import radians, cos, sin, sqrt, atan2
from django.db import IntegrityError
import random
from core.models import Doctor, SPECIALIZATIONS,  Review, Appointment
from django.utils import timezone
from .models import CounselingTest, TestQuestion, TestAnswer, TestResult
from django.contrib.auth.decorators import login_required, user_passes_test

# def is_doctor(user):
#     return hasattr(user, 'doctor')

# @user_passes_test(is_doctor)
# @login_required
# def doctor_dashboard(request):
#     doctor = request.user.doctor
#     appointments = Appointment.objects.filter(doctor=doctor)
#     return render(request, 'doctor_dashboard.html', {'appointments': appointments})
# from django.http import HttpResponseForbidden


def index(request):
    return render(request, 'index.html')


def generate_dummy_doctors():
    cities_lat_lon = [
        (28.6139, 77.2090),  # Delhi
        (19.0760, 72.8777),  # Mumbai
        (12.9716, 77.5946),  # Bangalore
        (22.5726, 88.3639),  # Kolkata
        (13.0827, 80.2707),  # Chennai
    ]

    for specialization, _ in SPECIALIZATIONS:
        for _ in range(5):
            lat, lon = random.choice(cities_lat_lon)
            try:
                Doctor.objects.create(
                    name=f"Dr. {random.choice(['Agarwal', 'Patel', 'Sharma', 'Mehta', 'Kapoor'])}",
                    specialization=specialization,
                    latitude=lat + random.uniform(-0.05, 0.05),
                    longitude=lon + random.uniform(-0.05, 0.05)
                )
            except IntegrityError:
                continue
    print("Dummy doctors generated successfully!")
    
HOSPITALS = [
    "Apollo Hospital", "Fortis Hospital", "AIIMS", "Max Healthcare",
    "Narayana Health", "Manipal Hospital", "Medanta Hospital",
    "KIMS Hospital", "Columbia Asia Hospital", "Artemis Hospital"
]

# Function to calculate distance (Haversine formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def search_doctors(request):
    if "clear" in request.GET:
        return redirect("core:search_doctors")

    specialization = request.GET.get('specialization', '').strip().lower()
    latitude = request.GET.get('latitude', '')
    longitude = request.GET.get('longitude', '')

    doctors = Doctor.objects.all()

    # Match user input to valid specialization from choices
    matched_specialization = None
    for spec_db, spec_user in SPECIALIZATIONS:
        if specialization == spec_user.lower() or specialization == spec_db.lower():
            matched_specialization = spec_db
            break

    if matched_specialization:
        doctors = doctors.filter(specialization=matched_specialization)

    filtered_doctors = list(doctors)  # fallback if no location is given or error happens

    if latitude and longitude:
        try:
            user_lat, user_lon = float(latitude), float(longitude)
            nearby_doctors = []
            for doctor in doctors:
                if doctor.latitude and doctor.longitude:
                    distance = calculate_distance(user_lat, user_lon, doctor.latitude, doctor.longitude)
                    if distance <= 20:
                        doctor.distance = round(distance, 2)
                        doctor.workplace = doctor.workplace or random.choice(HOSPITALS)
                        doctor.working_hours = doctor.working_hours or f"{random.randint(8, 12)} AM - {random.randint(3, 9)} PM"
                        nearby_doctors.append(doctor)
            if nearby_doctors:
                filtered_doctors = nearby_doctors  # Override only if nearby doctors are found
        except ValueError:
            pass  # If lat/lon parsing fails, fallback remains

    return render(request, 'search_doctors.html', {'doctors': filtered_doctors})

def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = doctor.reviews.all()
    return render(request, 'doctor_profile.html', {'doctor': doctor, 'reviews': reviews})

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')

        Appointment.objects.create(
            doctor=doctor,
            patient=request.user,  # ✅ logged-in user
            appointment_date=appointment_date,
            time=appointment_time  # ✅ field name is `time`
        )

        messages.success(request, 'Appointment booked successfully!')
        return redirect('core:doctor_profile', doctor_id=doctor.id)

    return render(request, 'book_appointment.html', {'doctor': doctor})

@login_required
# View to display the list of tests
def counseling_test_selection(request):
    tests = CounselingTest.objects.all()
    return render(request, 'counseling_test_selection.html', {'tests': tests})

# View to display detailed information for a specific counseling test
def counseling_test_detail(request, test_id):
    test = get_object_or_404(CounselingTest, pk=test_id)
    return render(request, 'counseling_test_detail.html', {'test': test})

# View to take a counseling test
@login_required
@login_required
def take_counseling_test(request, test_id):
    test = get_object_or_404(CounselingTest, id=test_id)
    questions = TestQuestion.objects.filter(test=test).order_by('id')[:10].prefetch_related('answers')

    if request.method == 'POST':
        total_score = 0
        for q in questions:
            selected_answer_id = request.POST.get(str(q.id))
            if selected_answer_id:
                answer = TestAnswer.objects.get(id=selected_answer_id)
                total_score += answer.score
        result_text = "Normal" if total_score < 30 else "Needs Attention"  # Example logic
        TestResult.objects.create(user=request.user, test=test, score=total_score, result_text=result_text)
        return redirect('core:test_result', test_id=test.id)
    
    return render(request, 'take_counseling_test.html', {'test': test, 'questions': questions})

# View to display the result after the test
@login_required
def test_result(request, test_id):
    test = get_object_or_404(CounselingTest, pk=test_id)
    result = TestResult.objects.filter(user=request.user, test=test).last()

    if not result:
        return redirect('core:take_counseling_test', test_id=test_id)

    return render(request, 'test_result.html', {'result': result, 'test': test})



@login_required
def profile_view(request):
  user = request.user
  user_profile, created = UserProfile.objects.get_or_create(user=request.user)

  if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        record_form = MedicalRecordForm(request.POST, request.FILES)

        
        
        if 'photo' in request.FILES:  # when updating profile photo
            if profile_form.is_valid():
                profile_form.save()
                return redirect('core:profile')

        if record_form.is_valid():
            record = record_form.save(commit=False)
            record.user = user
            record.save()

            return redirect('core:profile')  # important to refresh page after saving!

        else:
                print(profile_form.errors)
  else:
        user_form = UserChangeForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)
        record_form = MedicalRecordForm()

  appointments = Appointment.objects.filter(patient=user)
  test_results = user.testresult_set.all()  
  medical_records = MedicalRecord.objects.filter(user=request.user)# This can stay if it's linked

  return render(request, 'profile.html', {
        
        'user_form': user_form,
        'user_profile': user_profile,
        'profile_form': profile_form,
        'record_form': record_form,
        'appointments': appointments,
        'test_results': test_results,
        'medical_records': medical_records, 
    })




def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('core:login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('core:index')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('core:index')


@login_required
def upload_medical_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.user = request.user
            medical_record.save()
            return redirect('core:profile')
    else:
        form = MedicalRecordForm()
    return render(request, 'upload_medical_record.html', {'form': form})

@login_required
def delete_medical_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)

    if record.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this record.")

    record.delete()
    return redirect('core:profile')

# @login_required
# @user_passes_test(is_doctor)
# def appointment_action(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         if action == 'accept':
#             appointment.status = 'Accepted'
#             messages.success(request, 'Appointment accepted.')
#         elif action == 'reject':
#             appointment.status = 'Rejected'
#             messages.success(request, 'Appointment rejected.')
#         appointment.save()
#     return redirect('core:doctor_dashboard')