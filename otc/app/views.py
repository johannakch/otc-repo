from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from .forms import EventForm
from .utils import EventCalendar, get_year_dic, hasReservationRight, get_this_seasons_events, get_number_of_exts, week_magic
from .models import Event, GameTypeChoice

import datetime


def index(request):
    if request.method == 'POST':
        if 'next' in request.POST:
            current_date = get_next_week_from_request(request)
        elif 'prev' in request.POST:
            current_date = get_prev_week_from_request(request)
    else:
        current_date = datetime.date.today()
        request.session['current_week'] = (current_date.day, current_date.month, current_date.year)

    context = {}
    platz_1 = create_base_calendar(request.user, current_date, 1)
    platz_2 = create_base_calendar(request.user, current_date, 2)
    platz_3 = create_base_calendar(request.user, current_date, 3)

    context.update({
        'platz_3': mark_safe(platz_3),
        'platz_2': mark_safe(platz_2),
        'platz_1': mark_safe(platz_1),
    })

    return render(request, 'app/index.html', context)

def get_prev_week_from_request(request):
    d = request.session['current_week'][0]
    m = request.session['current_week'][1]
    y = request.session['current_week'][2]
    date_from_request = datetime.date(day=d, month=m, year=y)
    start_of_week = week_magic(date_from_request)[0]
    last_week = (datetime.datetime(start_of_week.year, start_of_week.month, start_of_week.day) - datetime.timedelta(days=1)).date()
    request.session['current_week'] = (last_week.day, last_week.month, last_week.year)
    current_date = last_week
    return current_date


def get_next_week_from_request(request):
    if request.session.has_key('current_week'):
        d = request.session['current_week'][0]
        m = request.session['current_week'][1]
        y = request.session['current_week'][2]
        date_from_request = datetime.date(day=d, month=m, year=y)
        end_of_week = week_magic(date_from_request)[1]
        next_week_start = (datetime.datetime(end_of_week.year, end_of_week.month, end_of_week.day) + datetime.timedelta(days=1)).date()
        request.session['current_week'] = (next_week_start.day, next_week_start.month, next_week_start.year)
        current_date = next_week_start
    else:
        end_of_week = week_magic(datetime.date.today())[1]
        next_week_start = (datetime.datetime(end_of_week.year, end_of_week.month, end_of_week.day) + datetime.timedelta(days=1)).date()
        request.session['current_week'] = (next_week_start.day, next_week_start.month, next_week_start.year)
        current_date = next_week_start
    return current_date


def create_base_calendar(request, today, courtnumber):
    cal = EventCalendar(request, courtnumber).formatweek(today, today.month, today.year)
    return cal


def add_event(request, year, month, day, hour):
    context = {}
    context['date'] = format_date(day, month, year)
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    # boolean der form und html verändert, je nachdem ob es ein basic user oder ein staff/superuser ist
    context['is_basic_user'] = iba
    context['user'] = str(request.user)
    einzel = None  # wert der sich merkt ob einzel oder doppelbutton oben im form gewählt wurde
    time_value = datetime.time(int(hour), 00)
    context[einzel] = True
    if request.method == 'POST':
        # initialwerte für duration je nach einzel oder doppel, wenn einer der buttons oben im form gedrückt wurde
        if 'einzel' in request.POST:
            context['einzel'] = True
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='einzel')
        elif 'doppel' in request.POST:
            context['einzel'] = False
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 2}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='doppel')
        else:
            updated_request = request.POST.copy()
            if iba:
                # type setzen aus vorheriger buttonauswahl
                if request.POST.get("einzel-selected", None):
                    updated_request.update({'type': 'Einzelspiel'})
                else:
                    updated_request.update({'type': 'Doppelspiel'})
            new_event_form = EventForm(updated_request, is_basic_user=iba, year=year, month=month, day=day,
                                       type='einzel')
            context['form'] = new_event_form
            # TODO: Wenn kein Mitspieler ausgewählt wird ist es doch auch ok oder? Warum required? -> Marius fragen
            if new_event_form.is_valid():
                new_event = new_event_form.save(commit=False)
                new_event.creator = request.user
                if iba:  # Für basic user immer Platznummer 3
                    new_event.number = 3
                    new_event.title = "Reserviert für"
                    # type setzen aus vorheriger buttonauswahl
                    if request.POST.get("einzel-selected", None):
                        new_event.type = "Einzelspiel"
                    else:
                        new_event.type = "Doppelspiel"
                new_event.day = datetime.date(year=int(year), month=int(month), day=int(day))
                new_event.save()
                new_event_form.save_m2m()
                # TODO: request.user sollte nicht in der Liste auswaehlbar sein und erst hier dem Event hinzugefuegt werden:
                return HttpResponseRedirect(reverse('index'))
            # TODO: Aussagekräftige Fehlermeldungens
    else:
        if (hasReservationRight(request.user, int(year), int(month), int(day))):
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='einzel')
        else:
            print("Error: No Reservationright")
            messages.info(request, 'Du hast in dieser Woche kein Recht mehr weitere Reservierungen vorzunehmen!')
            return HttpResponseRedirect(reverse('index'))
    # print(context['form'])
    return render(request, 'app/add_event.html', context)


def format_date(day, month, year):
    year_dic = get_year_dic()
    return '{}. {} {}'.format(day, year_dic[int(month)], year)


# TODO: email benachrichtigung bei delete
def show_event(request, id):
    if 'delete' in request.GET:
        id = int(request.GET.get('delete'))
        print('deletet event:' + str(request.GET.get('delete')))
        Event.objects.filter(id=id).delete()
        return HttpResponseRedirect(reverse('index'))
    context = {}
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    context['id'] = id
    event = Event.objects.get(id=id)
    players_list = [player.get_full_name() for player in event.players.all() if event.players.all()]
    context['players'] = players_list
    context['event'] = event
    # wenn aktueller user creator oder einer der players ist -> löschen anzeigen
    if (event.creator == request.user or len(Event.objects.filter(players__id=request.user.id)) > 0):
        context['is_member_of_event'] = True
    else:
        context['is_member_of_event'] = False
    return render(request, 'app/show_event.html', context)


def show_depts(request):
    context = {}
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    events = get_this_seasons_events(request.user)
    context['events'] = events
    number_of_exts = get_number_of_exts(events)
    context['exts'] = number_of_exts
    context['sum'] = number_of_exts * 5
    return render(request, 'app/show_depts.html', context)


def year_overview(request):
    context = {}
    type_list = [(type.value) for type in GameTypeChoice
                 if type.value != 'Einzelspiel'
                 if type.value != 'Doppelspiel'
                 if type.value != 'Training'
                 if type.value != 'Turnier']

    current_year = datetime.date.today().year
    general_events = Event.objects.filter(type__in=type_list, day__year=current_year).order_by('day', 'start_time')
    event_months_dic = {}
    for event in general_events:
        if event.day.month not in event_months_dic:
            event_months_dic[event.day.month] = [event]
        else:
            event_months_dic[event.day.month].append(event)

    context.update({
        'event_months_dic': event_months_dic,
    })
    return render(request, 'app/year_overview.html', context)