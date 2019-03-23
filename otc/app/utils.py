from calendar import HTMLCalendar
import datetime

from django.urls import reverse

from app.models import Event


class EventCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday, themonth, theyear, events, hour):
        """
        Return a day as a table cell.
        """
        events_from_day = events.filter(day__day=day)
        events_html = "<ul>"
        for event in events_from_day:
            events_html += event.get_absolute_url() + "<br>"
        events_html += "</ul>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            # check if date to show is in the past
            current_date = datetime.date(year=theyear, month=themonth, day=day)
            if current_date < datetime.date.today() or (current_date == datetime.date.today() and hour <= datetime.datetime.now().time().hour):
                return '<td class="%s">%s</td>' % (self.cssclasses[weekday], events_html)
            else:
                url = reverse('add_event', args=(theyear, themonth, day, hour))
                return '<td class="%s"><a href="%s">+</a>%s</td>' % (self.cssclasses[weekday], url, events_html)


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
            events = Event.objects.filter(day__lte=end).filter(day__gte=start).filter(start_time=str(i)+':00:00')
            s = ''.join(self.formatday(d, wd, m, y, events, i) for (d, wd, m, y) in theweek)
            if i < 10:
                a('<tr><th scope="row">0%s:00</th>%s</tr>' % (str(i), s))
            else:
                a('<tr><th scope="row">%s:00</th>%s</tr>' % (str(i), s))

        a('</table>')
        a('\n')
        table = ''.join(v)
        print("TABLE:", table)


        table = table.replace('<td ', '<td  width="150" height="60"')
        table = table.replace('<th class="mon">Mon</th><th class="tue">Tue</th>'
                              '<th class="wed">Wed</th><th class="thu">Thu</th>'
                              '<th class="fri">Fri</th><th class="sat">Sat</th>'
                              '<th class="sun">Sun</th>', '<td></td><th class="mon">Montag, '+str(theweek[0][0])+'</th>'
                              '<th class="mon">Dienstag, '+str(theweek[1][0])+'</th><th class="mon">Mittwoch, '+str(theweek[2][0])+'</th>'
                              '<th class="mon">Donnerstag, '+str(theweek[3][0])+'</th><th class="mon">Freitag, '+str(theweek[4][0])+'</th>'
                              '<th class="mon">Samstag, '+str(theweek[5][0])+'</th><th class="mon">Sonntag, '+str(theweek[6][0])+'</th>')
        return table


    def formatmonthname(self, theyear, themonth, withyear=True):
        year_dic =  get_year_dic()
        monthname = '<tr><th colspan="8" scope="col" class="month">%s %d</th><//tr>' % (year_dic[themonth], theyear)

        return monthname





def get_year_dic():
    return {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni", 7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"}

#falls user schon event in dieser woche hat -> gibt diese methode false zurück
def hasReservationRight(user, theyear, themonth, day):
    start, end = week_magic(datetime.date(year=theyear, month=themonth, day=day))
    weeklyevents = Event.objects.filter(day__range=[start, end])
    usersevents = weeklyevents.filter(creator=user)
    usersevents2 = weeklyevents.filter(players__id=user.id)
    return (not(len(usersevents)>0) and not(len(usersevents2)>0))

def week_magic(day):
       day_of_week = day.weekday()
       to_beginning_of_week = datetime.timedelta(days=day_of_week)
       beginning_of_week = day - to_beginning_of_week

       to_end_of_week = datetime.timedelta(days=6 - day_of_week)
       end_of_week = day + to_end_of_week

       return (beginning_of_week, end_of_week)