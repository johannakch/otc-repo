import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from app.forms import EventForm
from app.utils import EventCalendar, get_year_dic, hasReservationRight
from app.models import Event, GameTypeChoice


from django.contrib import messages

def index(request):
    context = {}
    today = datetime.date.today()
    platz_1 = create_base_calendar(request.user, today, 1)
    platz_2 = create_base_calendar(request.user, today, 2)
    platz_3 = create_base_calendar(request.user, today, 3)

    context.update({
        'platz_3': mark_safe(platz_3),
        'platz_2': mark_safe(platz_2),
        'platz_1': mark_safe(platz_1),
    })

    return render(request, 'app/index.html', context)

def create_base_calendar(request, today, courtnumber):
    cal = EventCalendar(request, courtnumber).formatweek(today, today.month, today.year)
    return cal

def add_event(request, year, month, day, hour):
   context = {}
   context['date'] = format_date(day, month, year)
   iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
   # boolean der form und html verändert, je nachdem ob es ein basic user oder ein staff/superuser ist
   context['is_basic_user'] = iba
   einzel = None # wert der sich merkt ob einzel oder doppelbutton oben im form gewählt wurde
   time_value = datetime.time(int(hour), 00)
   context[einzel] = True
   if request.method == 'POST':
       # initialwerte für duration je nach einzel oder doppel, wenn einer der buttons oben im form gedrückt wurde
       if 'einzel' in request.POST:
           context['einzel'] = True
           context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1}, is_basic_user=iba, year=year, month=month, day=day, type='einzel')
       elif 'doppel' in request.POST:
           context['einzel'] = False
           context['form'] = EventForm(initial={'start_time': time_value, 'duration': 2}, is_basic_user=iba, year=year, month=month, day=day, type='doppel')
       else:
           new_event_form = EventForm(request.POST, is_basic_user=iba, year=year, month=month, day=day, type='einzel')
           context['form'] = new_event_form
           if new_event_form.is_valid():
               new_event = new_event_form.save(commit=False)
               new_event.creator = request.user
               if iba: # Für basic user immer Platznummer 3
                   new_event.number = 3
                   # type setzen aus vorheriger buttonauswahl
                   if request.POST.get("einzel-selected", None):
                       new_event.type = "Einzelspiel"
                   else:
                       new_event.type = "Doppelspiel"
               new_event.title = "Reserviert für"
               new_event.day = datetime.date(year=int(year), month=int(month), day=int(day))
               new_event.save()
               new_event_form.save_m2m()
               # TODO: request.user sollte nicht in der Liste auswaehlbar sein und erst hier dem Event hinzugefuegt werden:
               # TODO: anzahl der ausgewählten mitspieler muss eingrenzt werden
               return HttpResponseRedirect(reverse('index'))
           # TODO: Aussagekräftige Fehlermeldungens
   else:
       if (hasReservationRight(request.user, int(year), int(month), int(day))):
           context['form'] = EventForm(initial={'start_time': time_value, 'duration': 1}, is_basic_user=iba, year=year, month=month, day=day, type='einzel')
       else:
           print("Error: No Reservationright")
           messages.info(request, 'Du hast in dieser Woche kein Recht mehr weitere Reservierungen vorzunehmen!')
           return HttpResponseRedirect(reverse('index'))
   print(context['form'])

   return render(request, 'app/add_event.html', context)


def format_date(day, month, year):
    year_dic = get_year_dic()
    return '{}. {} {}'.format(day, year_dic[int(month)], year)

# TODO: eventuell nur löschen statt edit für user die an der reservierung teilnehmen
def show_event(request, id):
    context = {}
    iba = (not (request.user.is_staff) and not (request.user.is_superuser) and request.user.is_active)
    context['id'] = id
    event = Event.objects.get(id=id)
    # wenn aktueller user creator oder einer der players ist -> bearbeitbares form anzeigen
    if (event.creator == request.user or len(Event.objects.filter(players__id=request.user.id))>0):
        context['is_basic_user'] = iba
        #context['form'] = EventForm(is_basic_user=iba, instance=event)
        context['form'] = EventForm(is_basic_user=iba, instance=event, year=2019, month=3, day=3)
        return render(request, 'app/add_event.html', context)
    else:
        players_list = [player.get_full_name() for player in event.players.all() if event.players.all()]
        context['players'] = players_list

        context['event'] = event


        return render(request, 'app/show_event.html', context)
