from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

from .forms import EventForm
from .utils import EventCalendar, get_year_dic, hasReservationRight, get_this_seasons_events, get_number_of_exts, week_magic, str_to_bool
from .models import Event, GameTypeChoice
from django.core.exceptions import ValidationError


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


def add_event(request, year, month, day, hour, pnumber):
    context = {}
    context['date'] = format_date(day, month, year)
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    # boolean der form und html verändert, je nachdem ob es ein basic user oder ein staff/superuser ist
    place_number = 3
    if not iba:
        place_number = pnumber
    context['is_basic_user'] = iba
    context['user'] = str(request.user)
    time_value = datetime.time(int(hour), 00)
    context['einzel'] = True # wert der sich merkt ob einzel oder doppelbutton oben im form gewählt wurde
    if request.method == 'POST':
        #print("POST")
        # initialwerte für duration je nach einzel oder doppel, wenn einer der buttons oben im form gedrückt wurde
        if 'einzel' in request.POST:
            #print("einzel selected")
            context['einzel'] = True
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1, 'number':place_number}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='einzel', number=place_number)
        elif 'doppel' in request.POST:
            #print("doppel selected")
            context['einzel'] = False
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 2, 'number':place_number}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='doppel', number=place_number)
        else:
            updated_request = request.POST.copy()
            new_event_form = EventForm(updated_request, is_basic_user=iba, year=year, month=month, day=day,
                                       type='einzel', number=place_number)
            if iba:
                einzel_selected = str_to_bool(request.POST.get("einzel-selected"))
                # type setzen aus vorheriger buttonauswahl
                if einzel_selected:
                    updated_request.update({'type': 'Einzelspiel',"title":'Reserviert für'})
                    new_event_form = EventForm(updated_request, is_basic_user=iba, year=year, month=month, day=day,
                                               type='einzel', number=place_number)
                else:
                    updated_request.update({'type': 'Doppelspiel',"title":'Reserviert für'})
                    new_event_form = EventForm(updated_request, is_basic_user=iba, year=year, month=month, day=day,
                                               type='doppel', number=place_number)
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
                try:
                    new_event.clean()
                    new_event.save()
                    new_event_form.save_m2m()
                    return HttpResponseRedirect(reverse('index'))
                except ValidationError as err:
                    print("Validation error: {0}".format(err))
                    messages.info(request,"Error: {0}".format(err))
                    return render(request, 'app/add_event.html', context)
            # TODO: Aussagekräftige Fehlermeldungens
    else:
        if (hasReservationRight(request.user, int(year), int(month), int(day))):
            context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1, 'number':place_number}, is_basic_user=iba, year=year,
                                        month=month, day=day, type='einzel', number=place_number)
        else:
            print("Error: No Reservationright")
            messages.info(request, 'Du hast in dieser Woche kein Recht mehr weitere Reservierungen vorzunehmen!')
            return HttpResponseRedirect(reverse('index'))
    # print(context['form'])
    return render(request, 'app/add_event.html', context)


def format_date(day, month, year):
    year_dic = get_year_dic()
    return '{}. {} {}'.format(day, year_dic[int(month)], year)


def show_event(request, id):
    context = {}
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    if 'delete' in request.POST:
        id = int(request.POST.get('delete'))
        print('deleted event: ID ' + str(request.POST.get('delete')))
        event_to_delete = Event.objects.filter(id=id)
        superusers = [user.email for user in User.objects.filter(is_superuser=True)]
        subject = 'Event wurde gelöscht!'
        von_name = request.user.get_full_name()
        message = '{} hat folgende Reservierung gelöscht: {}'.format(von_name,
                                                                     event_to_delete[0].title+', '+
                                                                     str(event_to_delete[0].day.strftime('%d.%m.%Y'))+', '+
                                                                     str(event_to_delete[0].start_time)+' Uhr')

        try:
            event_to_delete.delete()
            if iba:
                try:
                    email = EmailMessage(subject, message, to=superusers)
                    email.send()
                except Exception as exc:
                    print(exc)
                return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            print(e)
            msg = 'Die Reservierung konnte nicht gelöscht werden!'
            context.update({
                'delete_error': msg
            })
        return HttpResponseRedirect(reverse('index'))

    context['id'] = id
    event = Event.objects.get(id=id)
    players_list = [player.get_full_name() for player in event.players.all() if event.players.all()]
    if event.externPlayer1:
        players_list.append(event.externPlayer1)
    if event.externPlayer2:
        players_list.append(event.externPlayer2)
    if event.externPlayer3:
        players_list.append(event.externPlayer3)
    context['players'] = players_list
    context['creator'] = event.creator.get_full_name()
    context['event'] = event
    # wenn aktueller user creator oder einer der players ist -> löschen anzeigen
    ids = [player.id for player in event.players.all()]
    if event.creator == request.user or request.user.id in ids:
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
                 if type.value != 'Training']

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