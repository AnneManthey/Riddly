from django.contrib import admin
from .models import CalendarSettings, Door, DoorImage, UserDoorProgress


class DoorImageInline(admin.TabularInline):
    model = DoorImage
    extra = 1

class DoorAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'slug')
    search_fields = ('title', 'riddle')
    inlines = [DoorImageInline]


@admin.register(UserDoorProgress)
class UserDoorProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'door', 'solved', 'attempts', 'solved_at')
    list_filter = ('solved', 'user')
    list_select_related = ('user', 'door')
    actions = ['reset_progress']

    @admin.action(description="Fortschritt zurücksetzen (solved, solved_at, attempts)")
    def reset_progress(self, request, queryset):
        count = queryset.update(solved=False, solved_at=None, attempts=0)
        self.message_user(request, f"{count} Rätsel zurückgesetzt.")


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    list_display = ('date_restrictions_enabled',)

    def has_add_permission(self, request):
        return not CalendarSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Door, DoorAdmin)
