from django import forms
from django.utils import timezone

from .models import Event
from .models import GameTypeChoice
from .utils import hasReservationRight

import datetime

HOUR_CHOICES = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(8, 24)]


class EventForm(forms.ModelForm):
    #players = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                             #widget=CheckboxSelectMultiple(), required=False)

    def __init__(self, *args, **kwargs):
        is_basic_user = kwargs.pop('is_basic_user')
        y = kwargs.pop('year')
        m = kwargs.pop('month')
        d = kwargs.pop('day')
        selectedType = kwargs.pop('type')
        place_number = kwargs.pop('number')
        super(EventForm, self).__init__(*args, **kwargs)
        events = Event.objects.filter(day=datetime.date(year=int(y), month=int(m), day=int(d))).filter(number=place_number)
        eventTimes = [int(x.start_time.strftime("%H")) for x in events]
        # es sollten keine zeiten vor der aktuellen anklickbar sein,
        # wenn es um einen termin am aktuellen tag geht
        starthour = 8
        today = datetime.date.today()
        if (today.year==int(y) and today.month==int(m) and today.day==int(d)):
            starthour = timezone.now().hour+3
            if starthour>23:
                starthour = 23
        self.fields['start_time'].widget.choices = [(datetime.time(hour=x), '{:02d}:00'.format(x)) for x in range(starthour, 24)
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
        cleaned_players = cleaned_data.get('players')
        players = 0
        if cleaned_players is not None:
            current_date = datetime.date.today()
            has_no_reservation_right = [player for player in cleaned_players if not hasReservationRight(
                player, current_date.year, current_date.month, current_date.day)]

            if has_no_reservation_right:
                msg = "Folgende Spieler haben diese Woche bereits ihr Reservierungsrecht verbraucht: {}." \
                      " Wähle eine/n andere/n Mitspieler/in aus.".format(
                        ', '.join([player.first_name + ' ' + player.last_name for player in has_no_reservation_right]))
                self.add_error('players', msg)

            # print('Playerscount: '+str(len(cleaned_data.get('players'))))
            players = len(cleaned_players)
            if cleaned_data.get('type') == 'Einzelspiel':
                if len(cleaned_players) > 1:
                    msg = "Für ein Einzelspiel darf nicht mehr als ein Mitspieler ausgewählt werden!"
                    self.add_error('players', msg)
            if cleaned_data.get('type') == 'Doppelspiel':
                if len(cleaned_players) > 3:
                    msg = "Für ein Doppelspiel dürfen nicht mehr als drei Mitspieler ausgewählt werden!"
                    self.add_error('players', msg)

        exts = get_number_of_One_events_exts(cleaned_data)
        if cleaned_data.get('type') == 'Einzelspiel':
            if (players + exts) != 1:
                msg = "Für ein Einzelspiel muss genau ein Mitspieler ausgewählt werden! (Externer oder Interner)"
                self.add_error('players', msg)
        if cleaned_data.get('type') == 'Doppelspiel':
            if (players + exts) != 3:
                msg = "Für ein Doppelspiel müssen genau drei Mitspieler ausgewählt werden! (Beliebige Kombination aus Externen und Internen)"
                self.add_error('players', msg)


def get_number_of_One_events_exts(cleaned_data):
    count = 0
    if not cleaned_data.get('externPlayer1') == '':
        count = count + 1
    if not cleaned_data.get('externPlayer2') == '':
        count = count + 1
    if not cleaned_data.get('externPlayer3') == '':
        count = count + 1
    return count
