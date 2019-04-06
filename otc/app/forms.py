from django import forms
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple

from .models import Event
from .models import GameTypeChoice

import datetime

HOUR_CHOICES = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(8, 24)]


class EventForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                             widget=CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        is_basic_user = kwargs.pop('is_basic_user')
        y = kwargs.pop('year')
        m = kwargs.pop('month')
        d = kwargs.pop('day')
        selectedType = kwargs.pop('type')
        print(selectedType)
        super(EventForm, self).__init__(*args, **kwargs)
        events = Event.objects.filter(day=datetime.date(year=int(y), month=int(m), day=int(d)))
        eventTimes = [int(x.start_time.strftime("%H")) for x in events]

        self.fields['start_time'].widget.choices = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(8, 24)
                                                    if x not in eventTimes]
        if is_basic_user:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice if
                                           tag.value == "Einzelspiel" or tag.value == "Doppelspiel"]
            self.fields['duration'] = forms.IntegerField(min_value=1,max_value=2)
            if selectedType == 'einzel':
                self.fields['duration'] = forms.IntegerField(min_value=1, max_value=1)
                self.fields['type'].initial = 'Einzelspiel'
            if selectedType == 'doppel':
                self.fields['duration'] = forms.IntegerField(min_value=1,max_value=2)
        else:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice]
            self.fields['duration'] = forms.IntegerField(min_value=1,max_value=16)
            self.fields['type'].initial = 'Einzelspiel'

    class Meta:
        model = Event
        fields = (
            'title', 'type', 'start_time', 'players', 'duration', 'externPlayer1', 'externPlayer2', 'externPlayer3', 'number', 'notes')
        widgets = {'start_time': forms.Select(choices=HOUR_CHOICES)}

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get('players')==None):
            #print('Playerscount: '+str(len(cleaned_data.get('players'))))
            if cleaned_data.get('type')=='Einzelspiel':
                if (len(cleaned_data.get('players'))) > 1:
                    msg = "Für ein Einzelspiel darf nicht mehr als ein Mitspieler ausgewählt werden!"
                    self.add_error('players', msg)
            if cleaned_data.get('type')=='Doppelspiel':
                if (len(cleaned_data.get('players'))) > 3:
                    msg = "Für ein Doppelspiel dürfen nicht mehr als drei Mitspieler ausgewählt werden!"
                    self.add_error('players', msg)