from django.contrib import admin
from .models import Door

class DoorAdmin(admin.ModelAdmin):
    """ModelAdmin to view and filter the Door model."""
    list_display = ('number', 'title', 'solved', 'solved_at', 'user')
    list_filter = ('user', 'solved')
    list_select_related = ['user']

admin.site.register(Door, DoorAdmin)
