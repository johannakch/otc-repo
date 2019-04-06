from django.urls import reverse
from django.db.models import Q

from .models import Event

from calendar import HTMLCalendar
from copy import deepcopy
import datetime
from datetime import timedelta


class EventCalendar(HTMLCalendar):
    def __init__(self, user, courtnumber):
        super(EventCalendar, self).__init__()
        self.user = user
        self.courtnumber = courtnumber
        self.morethanonehour = []

    def formatday(self, day, weekday, themonth, theyear, events, hour):
        """
        Return a day as a table cell.
        """
        # default type-color
        type_color = '#ffc107'
        events_from_day = events.filter(day__day=day, number=self.courtnumber)
        events_html = ""
        is_start = False
        is_middle = False
        is_end = False
        for event in events_from_day:
            is_start = get_is_start(event)
            type_color = get_type_color(event.type)
            events_html += event.get_absolute_url(type_color) + "<br>"

        # check if there is a two hour game
        if events_html == '':
            for (ev, old_start_time) in self.morethanonehour:
                if ev.start_time.hour == hour and ev.day.year == theyear and ev.day.month == themonth and ev.day.day == day and ev.number == self.courtnumber:
                    type_color = get_type_color(ev.type)
                    is_middle = get_is_middle(ev, old_start_time)
                    is_end = get_is_end(ev, old_start_time)
                    events_html += ev.get_absolute_url(type_color) + "<br>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            return self.get_tablecell_content(theyear, themonth, day, hour, weekday, events_html, type_color, is_start, is_middle, is_end)

    def formatweek(self, today, themonth, theyear):
        """
        Return a complete week as a table row.
        """
        # startdate and enddate of current week
        start, end = week_magic(today)

        theweek = []
        for week in self.monthdatescalendar(theyear, themonth):
            if (week[0].day == start.day and week[-1].day == end.day):
                i = 0
                for date in week:
                    theweek.append((date.day, i, date.month, date.year))
                    i += 1

        if theweek == []:
            # initialize theweek with 0 values if no current week not found
            theweek = [(0, 0, 0, 0), (0, 1, 0, 0), (0, 2, 0, 0), (0, 3, 0, 0), (0, 4, 0, 0), (0, 5, 0, 0), (0, 6, 0, 0)]

        v = []
        a = v.append
        a('<table class="table-responsive table month" border="0" cellpadding="0" cellspacing="0">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=True))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for i in range(8, 24):
            events = Event.objects.filter(day__lte=end).filter(day__gte=start).filter(start_time=str(i) + ':00:00')
            for event in events:
                # checks if game is doppel AND two hours, because a Doppel can be also 1 hour
                # create copy of two hour event (without saving it to db)
                if event.duration > 1:
                    for h in range(1, event.duration):
                        new_time = (datetime.datetime(event.day.year, event.day.month, event.day.day) + timedelta(
                            hours=i + h)).time()
                        new_event = deepcopy(event)
                        new_event.start_time = new_time
                        self.morethanonehour.append((new_event, event.start_time))

            s = ''.join(self.formatday(d, wd, m, y, events, i) for (d, wd, m, y) in theweek)
            if i < 10:
                a('<tr><th scope="row">0%s:00</th>%s</tr>' % (str(i), s))
            else:
                a('<tr><th scope="row">%s:00</th>%s</tr>' % (str(i), s))

        a('</table>')
        a('\n')
        table = ''.join(v)
        # print("TABLE:", table)

        table = table.replace('<td ', '<td  width="150" height="60"')
        table = table.replace('<th class="mon">Mon</th><th class="tue">Tue</th>'
                              '<th class="wed">Wed</th><th class="thu">Thu</th>'
                              '<th class="fri">Fri</th><th class="sat">Sat</th>'
                              '<th class="sun">Sun</th>',
                              '<th></th><th class="mon">Montag, ' + str(theweek[0][0]) + '</th>'
                                                                                         '<th class="mon">Dienstag, ' + str(
                                  theweek[1][0]) + '</th><th class="mon">Mittwoch, ' + str(theweek[2][0]) + '</th>'
                                                                                                            '<th class="mon">Donnerstag, ' + str(
                                  theweek[3][0]) + '</th><th class="mon">Freitag, ' + str(theweek[4][0]) + '</th>'
                                                                                                           '<th class="mon">Samstag, ' + str(
                                  theweek[5][0]) + '</th><th class="mon">Sonntag, ' + str(theweek[6][0]) + '</th>')
        return table

    def formatmonthname(self, theyear, themonth, withyear=True):
        year_dic = get_year_dic()
        monthname = '<tr><th colspan="8" scope="col" class="month">%s %d / Platznr. %d</th></tr>' % (
            year_dic[themonth], theyear, self.courtnumber)

        return monthname

    def get_tablecell_content(self, theyear, themonth, day, hour, weekday, events_html, type_color, is_start, is_middle, is_end):
        # check if date to show is in the past
        current_date = datetime.date(year=theyear, month=themonth, day=day)
        admin_user = (self.user.is_superuser or self.user.is_staff) and (
                self.courtnumber == 3 or self.courtnumber == 2 or self.courtnumber == 1)
        active_user = self.user.is_active and not self.user.is_staff and not self.user.is_superuser and self.courtnumber == 3

        if is_time_in_path(hour, current_date):
            if events_html == '':
                return '<td class="%s">%s</td>' % (self.cssclasses[weekday], events_html)
            else:
                if is_start:
                    return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 0px 0px">%s</td>' % (
                        self.cssclasses[weekday], type_color['type'], events_html)
                elif is_middle:
                    return '<td class="%s" style="background-color: %s">%s</td>' % (
                        self.cssclasses[weekday], type_color['type'], events_html)
                elif is_end:
                    return '<td class="%s" style="background-color: %s; border-radius: 0px 0px 15px 15px">%s</td>' % (
                        self.cssclasses[weekday], type_color['type'], events_html)
                else:
                    return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 15px 15px">%s</td>' % (
                        self.cssclasses[weekday], type_color['type'], events_html)
        else:
            # if self.twohoursgame:
            #     events_html += self.twohoursgame.get_absolute_url() + "<br>"
            #     self.twohoursgame = None
            url = reverse('add_event', args=(theyear, themonth, day, hour))
            if admin_user:
                if events_html == '':
                    return '<td class="%s"><a href="%s" style="color: #2C3E50">+</a></td>' % (
                        self.cssclasses[weekday], url)
                else:
                    if is_start:
                        return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 0px 0px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    elif is_middle:
                        return '<td class="%s" style="background-color: %s">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    elif is_end:
                        return '<td class="%s" style="background-color: %s; border-radius: 0px 0px 15px 15px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    else:
                        return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 0px 0px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
            elif active_user:
                if events_html == '':
                    return '<td class="%s"><a href="%s" style="color: #2C3E50">+</a></td>' % (
                        self.cssclasses[weekday], url)
                else:
                    if is_start:
                        return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 0px 0px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    elif is_middle:
                        return '<td class="%s" style="background-color: %s">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    elif is_end:
                        return '<td class="%s" style="background-color: %s; border-radius: 0px 0px 15px 15px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
                    else:
                        return '<td class="%s" style="background-color: %s; border-radius: 15px 15px 0px 0px">%s</td>' % (
                            self.cssclasses[weekday], type_color['type'], events_html)
            else:
                return '<td class="%s">%s</td>' % (self.cssclasses[weekday], events_html)


def get_year_dic():
    return {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
            9: "September", 10: "Oktober", 11: "November", 12: "Dezember"}


# falls user schon event in dieser woche hat -> gibt diese methode false zurück
def hasReservationRight(user, theyear, themonth, day):
    start, end = week_magic(datetime.date(year=theyear, month=themonth, day=day))
    weeklyevents = Event.objects.filter(day__range=[start, end])
    usersevents = weeklyevents.filter(creator=user).filter(Q(type='Einzelspiel') or Q(type='Doppelspiel'))
    usersevents2 = weeklyevents.filter(players__id=user.id).filter(Q(type='Einzelspiel') or Q(type='Doppelspiel'))
    return (not (len(usersevents) > 0) and not (len(usersevents2) > 0))


def week_magic(day):
    day_of_week = day.weekday()
    to_beginning_of_week = datetime.timedelta(days=day_of_week)
    beginning_of_week = day - to_beginning_of_week

    to_end_of_week = datetime.timedelta(days=6 - day_of_week)
    end_of_week = day + to_end_of_week

    return (beginning_of_week, end_of_week)


def get_hours(event):
    '''
    Returns count of hours greater than 1 of an event
    '''
    return event.duration


def is_time_in_path(hour, current_date):
    if current_date < datetime.date.today() or (
            current_date == datetime.date.today() and hour <= datetime.datetime.now().time().hour):
        return True
    return False


def get_type_color(event_type):
    color_dict = {'Einzelspiel': {'type': '#D5F5E3', 'font': '#1D8348'},
                  'Doppelspiel': {'type': '#D5F5E3', 'font': '#1D8348'},
                  'Training': {'type': '#EBF5FB', 'font': '#2874A6'},
                  'Turnier': {'type': '#EBDEF0', 'font': '#6C3483'}, 'Event': {'type': '#FAD7A0', 'font': '#B9770E'},
                  'Arbeitseinsatz': {'type': '#FCF3CF', 'font': '#B7950B'},
                  'Medenrunde': {'type': '#FADBD8', 'font': '#B03A2E'}}
    return color_dict[event_type]

def get_is_start(event):
    if event.duration > 1:
        return True
    return False

def get_is_middle(ev, old_start_time):
    diff = (ev.start_time.hour - old_start_time.hour) + 1
    if diff < ev.duration:
        return True
    return False

def get_is_end(ev, old_start_time):
    diff = (ev.start_time.hour - old_start_time.hour) + 1
    if diff == ev.duration:
        return True
    return False

def get_this_seasons_events(user):
    today = datetime.date.today()
    yearstart = current_date = datetime.date(year=today.year, month=1, day=1)
    yearend = current_date = datetime.date(year=today.year, month=12, day=31)
    events_with_depts = Event.objects.filter(day__range=[yearstart, yearend]).filter(creator=user)
    return events_with_depts


def get_number_of_exts(events):
    count = 0
    for event in events:
        if not event.externPlayer1 == '':
            count = count + 1
        if not event.externPlayer2 == '':
            count = count + 1
        if not event.externPlayer3 == '':
            count = count + 1
    return count
