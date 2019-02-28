import datetime
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.utils.safestring import mark_safe

# Create your views here.
from app.forms import EventForm
from app.utils import EventCalendar, get_year_dic
from app.models import Event


def index(request):
    #print("REQUEST:",request.GET)
    context = {}
    today = datetime.date.today()
    cal = create_base_calendar(today)
    context['calendar'] = mark_safe(cal)

    return render(request, 'app/index.html', context)

def create_base_calendar(today):
    cal = EventCalendar().formatweek(today, today.month, today.year)
    return cal

def add_event(request, year, month, day):
    context = {}
    context['date'] = format_date(day, month, year)
    if request.method == 'POST':
        new_event_form = EventForm(request.POST)
        if new_event_form.is_valid():
            new_event = new_event_form.save(commit=False)
            new_event.day = datetime.date(year=int(year), month=int(month), day=int(day))
            new_event.save()
            new_event_form.save_m2m()
            # TODO: request.user sollte nicht in der Liste auswaehlbar sein und erst hier dem Event hinzugefuegt werden:
            # new_event.players.add(request.user)
            return HttpResponseRedirect(reverse('index'))
    else:
        context['form'] = EventForm()

    return render(request, 'app/add_event.html', context)

def format_date(day, month, year):
    year_dic = get_year_dic()
    return '{}. {} {}'.format(day, year_dic[int(month)], year)

def show_event(request, id):
    context = {}

    context['id'] = id
    event = Event.objects.get(id=id)

    players_list = [player.get_full_name() for player in event.players.all() if event.players.all()]
    context['players'] = players_list

    context['event'] = event

    return render(request, 'app/show_event.html', context)