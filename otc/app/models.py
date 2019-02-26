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
    trn_ezl = "Training (Einzel)"
    trn_dpl = "Training (Doppel)"
    trnr = "Turnier"
    ev = "Event"


class Event(models.Model):
    day = models.DateField(u'Tag', help_text=u'Tag der Reservierung')
    start_time = models.TimeField(u'Startzeit', help_text=u'Beginn der Reservierung')
    duration = models.PositiveSmallIntegerField(u'Dauer', help_text=u'Stundenanzahl', default=1, validators=[MaxValueValidator(12), MinValueValidator(1)])
    notes = models.TextField(u'Notizen', help_text=u'Beschreibung/Zusätzliche Infos', blank=True, null=True)
    title = models.CharField(u'Titel', max_length=200, help_text=u'Titel des Spiels')
    type = models.CharField(max_length=200, choices=[(tag.value, tag.value) for tag in GameTypeChoice]) #type=GameTypeChoice.trn_dpl
    players = models.ManyToManyField(User)
    number = models.PositiveSmallIntegerField(u'Platznummer', default=3, validators=[MaxValueValidator(3), MinValueValidator(1)]) #set min 1 max 3 default 3
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

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, str(self.start_time))

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