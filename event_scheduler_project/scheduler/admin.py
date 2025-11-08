from django.contrib import admin
from .models import AdminProfile, Category, Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'location')
    list_filter = ('start_time',)
    search_fields = ('title', 'description', 'location')

admin.site.register(AdminProfile)
admin.site.register(Category)
