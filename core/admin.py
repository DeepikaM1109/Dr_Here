from django.contrib import admin
from .models import Doctor, Appointment, CounselingTest

admin.site.register(Doctor)

admin.site.register(Appointment)
admin.site.register(CounselingTest)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('user',)  # Only show the image field

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', )

    def profile_image_preview(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.profile_image:
            return f'<img src="{obj.userprofile.profile_image.url}" style="height:40px;width:40px;border-radius:50%;" />'
        return ''
    profile_image_preview.allow_tags = True
    profile_image_preview.short_description = 'Profile'

# Unregister default User admin and register new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)