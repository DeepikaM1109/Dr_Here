from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from core.models import Appointment
from django.conf import settings

class Command(BaseCommand):
    help = 'Send reminders for today’s appointments'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        appointments = Appointment.objects.filter(appointment_date=today)

        for appointment in appointments:
            send_mail(
                subject='Appointment Reminder',
                message=f"Hi {appointment.patient.username}, you have an appointment today with Dr. {appointment.doctor.name} at {appointment.time}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient.email],
                fail_silently=False
            )
        self.stdout.write(self.style.SUCCESS('Reminders sent!'))
