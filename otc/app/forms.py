from django import forms
from django.contrib.auth.models import User

from app.models import Event

class EventForm(forms.ModelForm):


    class Meta:
        model = Event
        fields = ('title', 'type', 'start_time', 'players', 'number', 'duration',
                  'externPlayer1', 'externPlayer2', 'externPlayer3', 'notes')