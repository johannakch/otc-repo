import datetime
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.utils.safestring import mark_safe

# Create your views here.
from app.forms import EventForm
from app.utils import EventCalendar, get_year_dic, hasReservationRight
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
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    if request.method == 'POST':
        new_event_form = EventForm(request.POST, is_basic_user=iba)
        if new_event_form.is_valid():
            new_event = new_event_form.save(commit=False)
            new_event.creator = request.user
            new_event.number = 3
            new_event.title = "Reserviert für"
            new_event.day = datetime.date(year=int(year), month=int(month), day=int(day))
            new_event.save()
            new_event_form.save_m2m()
            # TODO: request.user sollte nicht in der Liste auswaehlbar sein und erst hier dem Event hinzugefuegt werden:
            # new_event.players.add(request.user)
            return HttpResponseRedirect(reverse('index'))
    else:
        if (hasReservationRight(request.user, int(year), int(month), int(day))):
            # boolean der form und html verändert, je nachdem ob es ein basic user oder ein staff/superuser ist
            context['is_basic_user'] = iba
            context['form'] = EventForm(is_basic_user=iba)
        else :
            print("Error: No Reservationright")
            return HttpResponseRedirect(reverse('index'))

    print(context['form'])

    return render(request, 'app/add_event.html', context)

def format_date(day, month, year):
    year_dic = get_year_dic()
    return '{}. {} {}'.format(day, year_dic[int(month)], year)

def show_event(request, id):
    context = {}
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    context['id'] = id
    event = Event.objects.get(id=id)
    # wenn aktueller user creator oder einer der players ist -> bearbeitbares form anzeigen
    if (event.creator == request.user or len(Event.objects.filter(players__id=request.user.id))>0):
        context['is_basic_user'] = iba
        context['form'] = EventForm(is_basic_user=iba, instance=event)
        return render(request, 'app/add_event.html', context)
    else:
        players_list = [player.get_full_name() for player in event.players.all() if event.players.all()]
        context['players'] = players_list

        context['event'] = event

        return render(request, 'app/show_event.html', context)