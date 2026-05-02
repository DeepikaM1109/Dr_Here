from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
   
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('search_doctors/', views.search_doctors, name='search_doctors'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('book_appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('doctor/<int:doctor_id>/book/', views.book_appointment, name='book_appointment'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/upload_record/', views.upload_medical_record, name='upload_medical_record'),
    path('profile/delete_record/<int:record_id>/', views.delete_medical_record, name='delete_medical_record'),
    path('counseling/', views.counseling_test_selection, name='counseling'),
    path('counseling-tests/', views.counseling_test_selection, name='counseling_test_selection'),
    path('counseling-tests/<int:test_id>/', views.take_counseling_test, name='take_counseling_test'),
    path('counseling-tests/<int:test_id>/result/', views.test_result, name='test_result'),
    path('counseling/<int:test_id>/', views.counseling_test_detail, name='counseling_test_detail'),
    # path('doctor/appointment/<int:appointment_id>/action/', views.appointment_action, name='appointment_action'),

]
