from django import forms
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple
from django.forms import Select

from app.models import Event
from app.models import GameTypeChoice

class EventForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                             widget = CheckboxSelectMultiple(), required=True)

    def __init__(self, *args, **kwargs):
        is_basic_user = kwargs.pop('is_basic_user')
        super(EventForm, self).__init__(*args, **kwargs)
        print("Basic" + str(is_basic_user))
        if is_basic_user:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice if tag.value == "Einzelspiel" or tag.value == "Doppelspiel"]
        else:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice]

    class Meta:
        model = Event
        fields = ('type', 'start_time', 'players', 'duration', 'externPlayer1', 'externPlayer2', 'externPlayer3', 'notes')
