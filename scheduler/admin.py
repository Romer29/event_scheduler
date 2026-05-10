from django.contrib import admin
from .models import AdminProfile, Category, Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'location', 'status', 'created_by')
    list_filter = ('status', 'start_time',)
    search_fields = ('title', 'description', 'location')

    # ✅ Optional: make status editable directly in list view
    list_editable = ('status',)

    # ✅ Optional: sort events by most recent
    ordering = ('-start_time',)
    
admin.site.register(AdminProfile)
admin.site.register(Category)
