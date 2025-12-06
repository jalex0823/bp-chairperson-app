"""
Generate a sample ICS file for Back Porch meetings based on the website schedule.
This is useful for local development/testing of the ICS import.

Schedule:
- Daily Literature-based Meeting: every day at 17:30 MT
- Women's Meeting: Saturdays at 08:30 MT
- Co-ed Meeting: Sundays at 08:30 MT
- Men's Meeting: Sundays at 15:30 MT

The script will generate concrete events for the next 12 weeks from today.
"""
from datetime import datetime, date, time, timedelta
from icalendar import Calendar, Event
import os

OUTPUT_PATH = os.path.join('resources', 'backporch-sample.ics')

# Helper to iterate dates for next N weeks on specific weekday
# weekday: Monday=0 ... Sunday=6

def iter_weekdays(start: date, weekday: int, weeks: int):
    # Find the first target weekday on/after start
    days_ahead = (weekday - start.weekday()) % 7
    d = start + timedelta(days=days_ahead)
    for _ in range(weeks):
        yield d
        d += timedelta(days=7)


def main():
    weeks = 12
    today = date.today()

    cal = Calendar()
    cal.add('prodid', '-//Back Porch Meetings//backporchmeetings.org//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Back Porch Sample Schedule')

    # Daily meeting: every day at 17:30
    for i in range(weeks * 7):
        d = today + timedelta(days=i)
        start_dt = datetime.combine(d, time(hour=17, minute=30))
        end_dt = start_dt + timedelta(hours=1)
        ev = Event()
        ev.add('summary', 'Daily Literature-based Meeting')
        ev.add('dtstart', start_dt)
        ev.add('dtend', end_dt)
        ev.add('location', 'Online')
        ev.add('description', 'AA-approved literature only')
        ev.add('uid', f'daily-{d.isoformat()}@backporchmeetings.org')
        cal.add_component(ev)

    # Women's Meeting: Saturday 08:30
    for d in iter_weekdays(today, 5, weeks):  # Saturday=5
        start_dt = datetime.combine(d, time(hour=8, minute=30))
        end_dt = start_dt + timedelta(hours=1)
        ev = Event()
        ev.add('summary', "Women's Meeting")
        ev.add('dtstart', start_dt)
        ev.add('dtend', end_dt)
        ev.add('location', 'Online')
        ev.add('description', 'Women only')
        ev.add('uid', f'women-{d.isoformat()}@backporchmeetings.org')
        cal.add_component(ev)

    # Co-ed Meeting: Sunday 08:30
    for d in iter_weekdays(today, 6, weeks):  # Sunday=6
        start_dt = datetime.combine(d, time(hour=8, minute=30))
        end_dt = start_dt + timedelta(hours=1)
        ev = Event()
        ev.add('summary', 'Co-ed Meeting')
        ev.add('dtstart', start_dt)
        ev.add('dtend', end_dt)
        ev.add('location', 'Online')
        ev.add('description', 'Co-ed')
        ev.add('uid', f'coed-{d.isoformat()}@backporchmeetings.org')
        cal.add_component(ev)

    # Men's Meeting: Sunday 15:30
    for d in iter_weekdays(today, 6, weeks):  # Sunday=6
        start_dt = datetime.combine(d, time(hour=15, minute=30))
        end_dt = start_dt + timedelta(hours=1)
        ev = Event()
        ev.add('summary', "Men's Meeting")
        ev.add('dtstart', start_dt)
        ev.add('dtend', end_dt)
        ev.add('location', 'Online')
        ev.add('description', 'Men only')
        ev.add('uid', f'men-{d.isoformat()}@backporchmeetings.org')
        cal.add_component(ev)

    # Write out
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'wb') as f:
        f.write(cal.to_ical())

    print(f'Wrote sample ICS: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
