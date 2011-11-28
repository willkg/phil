######################################################################
# This file is part of phil.
#
# Copyright (C) 2011 Will Kahn-Greene
#
# phil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# phil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with phil.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################


import datetime
import dateutil.rrule

from phil.configuration import parse_configuration
from phil.util import err, normalize_path, DIR, load_state, save_state
from icalendar import Calendar, vDatetime, vText


# TODO: If we don't do anything with events, turn it into a 
# namedtuple.
class Event(object):
    def __init__(self, event_id, rrule, summary='', description='',
                 organizer='', url=''):
        self.event_id = event_id
        self.rrule = rrule
        self.summary = summary
        self.description = description
        self.organizer = organizer
        self.url = url

    def __repr__(self):
        return "<Event %r %s>" % (self.rrule, self.summary)


FREQ_MAP = {
    # TODO: Make sure this covers all of them.
    'HOURLY': dateutil.rrule.HOURLY,
    'DAILY': dateutil.rrule.DAILY,
    'MONTHLY': dateutil.rrule.MONTHLY,
    'YEARLY': dateutil.rrule.YEARLY
    }


def convert_rrule(rrule):
    """Converts icalendar rrule to dateutil rrule."""
    args = {}

    # TODO: rrule['freq'] is a list, but I'm unclear as to why.
    freq = FREQ_MAP[rrule['freq'][0]]

    keys = ['wkst', 'until', 'bysetpos', 'interval',
            'bymonth', 'bymonthday', 'byyearday', 'byweekno',
            'byweekday', 'byhour', 'byminute', 'bysecond']
    args = dict((key, rrule.get(key)) for key in keys)

    return freq, args


def parse_ics(icsfile):
    """Takes an icsfilename, parses it, and returns Events."""
    events = []

    cal = Calendar.from_string(open(icsfile, 'rb').read())
    for component in cal.walk('vevent'):
        dtstart = vDatetime.from_ical(str(component['dtstart']))
        rrule = component['rrule']

        freq, args = convert_rrule(rrule)
        args['dtstart'] = dtstart

        rrule = dateutil.rrule.rrule(freq, **args)

        keys = ['summary', 'description', 'organizer', 'url']

        args = dict((key, vText.from_ical(component.get(key, u'')))
                    for key in keys)

        # TODO: Find an event id.  If it's not there, then compose one
        # with dtstart, summary, and organizer.
        event_id = "::".join(
            (str(dtstart),
             args.get('summary', 'None'),
             args.get('organizer', 'None')))

        events.append(Event(event_id, rrule, **args))
    return events


def should_remind(remind, rrule, dtstart=None):
    if dtstart == None:
        dtstart = datetime.datetime.today()

    nextdate = rrule.after(dtstart, inc=True)
    delta = nextdate - dtstart
    return remind == delta.days


def handle_section(section, cfg):
    # TODO: These override default section defaults.
    # TODO: Handle absence of variables.
    icsfile = normalize_path(cfg.get(section, 'icsfile'))
    datadir = normalize_path(cfg.get(section, 'datadir'), DIR)
    remind = int(cfg.get(section, 'remind'))

    # TODO: Catch exceptions with state loading here.
    state = load_state(datadir)

    today = datetime.date.today()
    events = parse_ics(icsfile)
    for event in events:
        if should_remind(remind, today, event.rrule):
            print "REMIND ME!"

    save_state(datadir, state)


def check_for_events(conf):
    cfg = parse_configuration(conf)

    try:
        for section in cfg.sections():
            handle_section(section, cfg)
    except Exception, e:
        import traceback
        print "".join(traceback.format_exc())
        err('%s (%r)' % (e, e))
        return 1

    print "done!"
    return 0
