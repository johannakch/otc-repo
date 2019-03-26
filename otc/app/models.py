# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
import datetime
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
    creator = models.ForeignKey(User, related_name='creator', null=True)
    day = models.DateField(u'Datum', help_text=u'Tag der Reservierung')
    start_time = models.TimeField(u'Startzeit', help_text=u'Beginn der Reservierung')
    duration = models.PositiveSmallIntegerField(u'Dauer', help_text=u'Stundenanzahl')
    notes = models.TextField(u'Notizen', help_text=u'Beschreibung/Zusätzliche Infos', blank=True, null=True)
    title = models.CharField(u'Titel', max_length=200, help_text=u'Titel des Spiels')
    type = models.CharField(u'Einzel/Doppel', max_length=200, choices=[(tag.value, tag.value) for tag in GameTypeChoice], help_text=u'Art des Trainings', blank=True) #type=GameTypeChoice.trn_dpl
    players = models.ManyToManyField(User, related_name='otherplayers', verbose_name=u'Spieler', blank=True, help_text=u'Wähle dich und deine/n Mitspieler aus')
    number = models.PositiveSmallIntegerField(u'Platznummer', default=3, validators=[MaxValueValidator(3), MinValueValidator(1)], help_text=u'Nummer des Tennisplatzes', blank=True) #set min 1 max 3 default 3
    externPlayer1 = models.CharField(u'Externer 1', max_length=200, help_text='Name des ersten externen Mitspielers (falls vorhanden)', blank=True)
    externPlayer2 = models.CharField(u'Externer 2', max_length=200, help_text='Name des zweiten externen Mitspielers (falls vorhanden)', blank=True)
    externPlayer3 = models.CharField(u'Externer 3', max_length=200, help_text='Name des dritten externen Mitspielers (falls vorhanden)',blank=True)


    class Meta:
        verbose_name = u'Reservierung'
        verbose_name_plural = u'Reservierungen'

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (
                new_end >= fixed_start and new_end <= fixed_end):  # innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True

        return overlap

    def get_absolute_url(self, type_color):
        url = reverse('show_event', args=[self.id])
        return u'<a href="%s" style="color: %s">%s</a>' % (url, type_color['font'],self.title + ': ' +', '.join([p.get_full_name() for p in self.players.all()]))

    def clean(self):
        events = Event.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if self.check_overlap(event.start_time, event.get_end_time(), self.start_time, self.get_end_time()):
                    raise ValidationError(
                        'Leider überschneidet sich die Reservierung mit einer anderen: ' + str(event.day) + ', ' + str(
                            event.start_time) + '-' + str(event.get_end_time()))

    def get_end_time(self):
        return self.start_time.replace(hour=(self.start_time.hour+self.duration))

    def __str__(self):
        return self.title