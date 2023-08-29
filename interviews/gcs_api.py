from datetime import datetime

from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from gcsa.attendee import Attendee
from gcsa.google_calendar import GoogleCalendar
from gcsa.calendar import Calendar



calendar = GoogleCalendar('osms.opallios@gmail.com')


for event in calendar:
    print(event)

attendee = Attendee(
    'kuriwaln@opallios.com',
    display_name='Naresh khuriwal',
    additional_guests=3
)

event = Event(
    'Interview is created by Naresh',
    start=datetime(2022, 12, 12, 23, 0),
    location='Jaipur 468/21',
    minutes_before_popup_reminder=15,
    attendees=attendee
)
calendar.add_event(event)

gc = GoogleCalendar()


calendar = Calendar(
    'Travel calendar',
    description = 'Calendar for travel related events'
)
calendar = gc.add_calendar(calendar)

