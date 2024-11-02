from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_approved']
    list_filter = ['role', 'is_approved']
    actions = ['approve_technicians']

    def approve_technicians(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected technicians have been approved.")
    approve_technicians.short_description = "Approve selected technicians"

# Register your models here.
