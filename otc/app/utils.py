from calendar import HTMLCalendar
import datetime

from django.urls import reverse

from app.models import Event


class EventCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday, themonth, theyear, events):
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
            if current_date < datetime.date.today():
                return '<td class="%s">%d%s</td>' % (self.cssclasses[weekday], day, events_html)
            else:
                url = reverse('add_event', args=(theyear, themonth, day))
                return '<td class="%s"><a href="%s">%d</a>%s</td>' % (self.cssclasses[weekday], url, day, events_html)


    def formatweek(self, today, themonth, theyear):
        """
        Return a complete week as a table row.
        """
        # startdate and enddate of current week
        start, end = self.week_magic(today)


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

        # get all Events during the current week
        events = Event.objects.filter(day__lte=end).filter(day__gte=start)

        v = []
        a = v.append
        a('<div class="table-responsive">')
        a('<table class="table month" border="0" cellpadding="0" cellspacing="0">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=True))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        s = ''.join(self.formatday(d, wd, m, y, events) for (d, wd, m, y) in theweek)
        a('<tr>%s</tr>' % s)

        a('</table>')
        a('</div>')
        a('\n')
        table = ''.join(v)
        print("TABLE:", table)


        table = table.replace('<td ', '<td  width="150" height="100"')
        table = table.replace('<th class="mon">Mon</th><th class="tue">Tue</th>'
                              '<th class="wed">Wed</th><th class="thu">Thu</th>'
                              '<th class="fri">Fri</th><th class="sat">Sat</th>'
                              '<th class="sun">Sun</th>', '<th class="mon">Montag</th>'
                              '<th class="mon">Dienstag</th><th class="mon">Mittwoch</th>'
                              '<th class="mon">Donnerstag</th><th class="mon">Freitag</th>'
                              '<th class="mon">Samstag</th><th class="mon">Sonntag</th>')
        return table


    def formatmonthname(self, theyear, themonth, withyear=True):
        year_dic = {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni", 7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"}
        monthname = '<tr><th colspan="7" scope="col" class="month">%s %d</th><//tr>' % (year_dic[themonth], theyear)

        return monthname


    def week_magic(self, day):
        day_of_week = day.weekday()

        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = day - to_beginning_of_week

        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = day + to_end_of_week

        return (beginning_of_week, end_of_week)