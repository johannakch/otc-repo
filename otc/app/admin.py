from django.contrib import admin

# Register your models here.
from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'title', 'number')

admin.site.register(Event, EventAdmin)