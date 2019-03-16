from django import forms
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple
import datetime
HOUR_CHOICES = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(8, 24)]
from app.models import Event
from app.models import GameTypeChoice

class EventForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                             widget = CheckboxSelectMultiple(), required=True)

    def __init__(self, *args, **kwargs):
        is_basic_user = kwargs.pop('is_basic_user')
        y = kwargs.pop('year')
        m = kwargs.pop('month')
        d = kwargs.pop('day')
        super(EventForm, self).__init__(*args, **kwargs)
        events = Event.objects.filter(day=datetime.date(year=int(y), month=int(m), day=int(d)))
        eventTimes = [int(x.start_time.strftime("%H")) for x in events]
        times = [x for x in range(9,24) if x not in eventTimes]
        print(times[1])
        self.fields['start_time'].widget.choices = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(9, 24) if x not in eventTimes]
        if is_basic_user:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice if tag.value == "Einzelspiel" or tag.value == "Doppelspiel"]
        else:
            self.fields['type'].choices = [(tag.value, tag.value) for tag in GameTypeChoice]

    class Meta:
        model = Event
        fields = ('type', 'start_time', 'players', 'duration', 'externPlayer1', 'externPlayer2', 'externPlayer3', 'notes')
        widgets = {'start_time': forms.Select(choices=HOUR_CHOICES)}
