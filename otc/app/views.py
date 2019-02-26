import datetime
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from calendar import HTMLCalendar

from django.urls import reverse
from django.utils.safestring import mark_safe

# Create your views here.
from app.forms import EventForm
from app.utils import EventCalendar
from app.models import Event


def index(request):
    context = {}
    cal = create_base_calendar()
    context['calendar'] = mark_safe(cal)
    return render(request, 'app/index.html', context)

def create_base_calendar():
    today = datetime.date.today()
    cal = EventCalendar()
    week = cal.monthdays2calendar(today.year, today.month)
    week = today.isocalendar()[1]
    html_calendar = cal.formatweek(today, today.month, today.year)
    html_calendar = html_calendar.replace('<td ', '<td  width="150" height="100"')
    return html_calendar

def add_event(request, year, month, day):
    context = {}
    context['date'] = '{}.{}.{}'.format(day, month, year)
    if request.method == 'POST':
        new_event_form = EventForm(request.POST)
        if new_event_form.is_valid():
            new_event = new_event_form.save(commit=False)
            new_event.day = datetime.date(year=int(year), month=int(month), day=int(day))
            new_event.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        context['form'] = EventForm()

    return render(request, 'app/add_event.html', context)