# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as user

from enum import Enum

User = get_user_model()


class GameTypeChoice(Enum):   # A subclass of Enum
    trn_ezl = "Einzelspiel"
    trn_dpl = "Doppelspiel"
    trnr = "Turnier" # z.B: Herren 1 gegen Herren 2
    ev = "Event"
    ab = "Arbeitseinsatz"
    mr = "Medenrunde"
    trn = "Training"

class Event(models.Model):
    creator = models.ForeignKey(User, related_name='creator', null=True, on_delete=models.SET_NULL)
    day = models.DateField(u'Datum', help_text=u'Tag der Reservierung')
    start_time = models.TimeField(u'Startzeit', help_text=u'Beginn der Reservierung')
    duration = models.PositiveSmallIntegerField(u'Dauer', help_text=u'Stundenanzahl')
    notes = models.TextField(u'Notizen', help_text=u'Beschreibung/Zusätzliche Infos', blank=True, null=True)
    title = models.CharField(u'Titel', max_length=200, help_text=u'Titel des Spiels')
    type = models.CharField(u'Event-Typ', max_length=200, choices=[(tag.value, tag.value) for tag in GameTypeChoice], help_text=u'Art des Trainings') #type=GameTypeChoice.trn_dpl
    players = models.ManyToManyField(User, related_name='otherplayers', verbose_name=u'Spieler', blank=True, help_text=u'Wähle deine/n Mitspieler aus')
    number = models.PositiveSmallIntegerField(u'Platznummer', default=3, validators=[MaxValueValidator(3), MinValueValidator(1)], help_text=u'Nummer des Tennisplatzes', blank=True) #set min 1 max 3 default 3
    externPlayer1 = models.CharField(u'Externer 1', max_length=200, help_text='Name des ersten externen Mitspielers (falls vorhanden)', blank=True)
    externPlayer2 = models.CharField(u'Externer 2', max_length=200, help_text='Name des zweiten externen Mitspielers (falls vorhanden)', blank=True)
    externPlayer3 = models.CharField(u'Externer 3', max_length=200, help_text='Name des dritten externen Mitspielers (falls vorhanden)',blank=True)


    class Meta:
        verbose_name = u'Reservierung'
        verbose_name_plural = u'Reservierungen'

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end, fixed_number, new_number):
        if not fixed_number == new_number:
            return False
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (
                new_end >= fixed_start and new_end <= fixed_end):  # start within fixed or end within fixed
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True
        return overlap

    def get_absolute_url(self, type_color, cur_user, is_start):
        url = reverse('show_event', args=[self.id])
        return u'<a href="%s" style="color: %s">%s<br/>%s%s</a>' \
               % (url, type_color['font'], get_title(self, is_start), get_time(self, is_start), get_player_names(self, [p for p in self.players.all()], cur_user, is_start))

    def clean(self):
        events = Event.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if event is self:
                    print(self)
                if self.check_overlap(event.start_time, event.get_end_time(), self.start_time, self.get_end_time(), event.number, self.number):
                    raise ValidationError(
                        'Leider überschneidet sich die Reservierung mit einer anderen: ' + str(event.day.strftime("%d-%m-%Y")) + ', ' + str(
                            event.start_time) + '-' + str(event.get_end_time()))


    def get_end_time(self):
        print(self.start_time.hour+self.duration)
        if self.start_time.replace(hour=(self.start_time.hour+self.duration)).hour > 23:
            return 23
        return self.start_time.replace(hour=(self.start_time.hour+self.duration))

    def __str__(self):
        return self.title


def get_player_names(event, players, cur_user, is_start):
    type_list = ['Einzelspiel', 'Doppelspiel']
    player_list = [player.get_full_name() for player in players if event.type in type_list]
    if event.externPlayer1:
        player_list.append(event.externPlayer1)
    if event.externPlayer2:
        player_list.append(event.externPlayer2)
    if event.externPlayer3:
        player_list.append(event.externPlayer3)

    if player_list == [] or (not is_start and event.duration > 1):
        return ''
    player_list.append(event.creator.get_full_name())
    return ': '+', '.join(sorted(player_list))

def get_time(event, is_start):
    if is_start or event.duration == 1:
        return str(event.start_time.strftime('%H:%M'))+'-'+str(event.start_time.hour+event.duration)+':'+str(event.start_time.strftime('%M'))
    return ''

def get_title(event, is_start):
    if is_start or event.duration == 1:
        return event.title
    return ''