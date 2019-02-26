from calendar import HTMLCalendar
import datetime

from django.urls import reverse

from app.models import Event


class EventCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday, events, themonth, theyear):
        """
        Return a day as a table cell.
        """
        events_from_day = events.filter(day__day=day)
        events_html = "<ul>"
        for event in events_from_day:
            events_html += event.get_absolute_url() + "<br>"
        events_html += "</ul>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            url = reverse('add_event', args=(theyear, themonth, day))
            return '<td class="%s"><a href="%s">%d</a>%s</td>' % (self.cssclasses[weekday], url, day, events_html)


    def formatweek(self, theday, themonth, theyear):
        """
        Return a complete week as a table row.
        """

        start, end = self.week_magic(theday)
        #theweek = 0
        for week in self.monthdays2calendar(theyear, themonth):
            if (week[0][0] == start.day or week[-1][0] == end.day):
                theweek = week
        events = Event.objects.filter(day__lte=end).filter(day__gte=start)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=True))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        s = ''.join(self.formatday(d, wd, events, themonth, theyear) for (d, wd) in theweek)
        a('<tr>%s</tr>' % s)

        a('</table>')
        a('\n')
        return ''.join(v)


    def week_magic(self, day):
        day_of_week = day.weekday()

        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = day - to_beginning_of_week

        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = day + to_end_of_week

        return (beginning_of_week, end_of_week)