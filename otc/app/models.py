# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum
from django.contrib.auth import get_user_model
User = get_user_model()

class GameTypeChoice(Enum):   # A subclass of Enum
    trn_dpl = "Training (Doppel)"
    trn_ezl = "Training (Einzel)"
    trnr = "Turnier"
    ev = "Event"

class Event(models.Model):
    day = models.DateField(u'Tag', help_text=u'Tag der Reservierung')
    start_time = models.TimeField(u'Stratzeit', help_text=u'Beginn der Reservierung')
    duration = models.PositiveSmallIntegerField(u'Dauer', help_text=u'Stundenanzahl', default=1, validators=[MaxValueValidator(12), MinValueValidator(1)])
    notes = models.TextField(u'Notizen', help_text=u'Beschreibung/Zusätzliche Infos', blank=True, null=True)
    title = models.CharField(u'Titel', max_length=200)
    type = models.CharField(max_length=5, choices=[(tag, tag.value) for tag in GameTypeChoice]) #type=GameTypeChoice.trn_dpl
    players = models.ManyToManyField(User)
    number = models.PositiveSmallIntegerField(default=3, validators=[MaxValueValidator(3), MinValueValidator(1)]) #set min 1 max 3 default 3
    externPlayer1 = models.CharField(u'Externer1', max_length=200, help_text='Name des ersten externen Mitspielers', blank=True)
    externPlayer2 = models.CharField(u'Externer2', max_length=200, help_text='Name des zweiten externen Mitspielers', blank=True)
    externPlayer3 = models.CharField(u'Externer3', max_length=200, help_text='Name des dritten externen Mitspielers',blank=True)


    class Meta:
        verbose_name = u'Reservierung'
        verbose_name_plural = u'Reservierungen'