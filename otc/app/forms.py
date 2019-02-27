from django import forms
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple
from django.forms import Select

from app.models import Event

class EventForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                             widget = CheckboxSelectMultiple(), required=True)

    class Meta:
        model = Event
        fields = ('title', 'type', 'start_time', 'players', 'number', 'duration', 'externPlayer1', 'externPlayer2', 'externPlayer3', 'notes')
