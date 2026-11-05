from django.contrib import admin
from .models import Door

class DoorAdmin(admin.ModelAdmin):
    """ModelAdmin to view and filter the Door model."""
    list_display = ('number', 'title', 'solved', 'solved_at', 'attempts', 'user')
    list_filter = ('user', 'solved')
    list_select_related = ['user']
    actions = ['reset_progress']

    @admin.action(description="Fortschritt zurücksetzen (solved, solved_at, attempts)")
    def reset_progress(self, request, queryset):
        count = queryset.update(solved=False, solved_at=None, attempts=0)
        self.message_user(request, f"{count} Rätsel zurückgesetzt.")

admin.site.register(Door, DoorAdmin)
