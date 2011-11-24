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


import os
import datetime
import dateutil.rrule
import json

from phil.configuration import parse_configuration
from phil.util import err, normalize_path, DIR
from icalendar import Calendar, vDatetime, vText


class Event(object):
    def __init__(self, rrule, summary='', description='', organizer='',
                 url=''):
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
        dtstart = component['dtstart']
        rrule = component['rrule']

        freq, args = convert_rrule(rrule)
        args['dtstart'] = vDatetime.from_ical(str(dtstart))

        rrule = dateutil.rrule.rrule(freq, **args)

        keys = ['summary', 'description', 'organizer', 'url']
        args = dict((key, vText.from_ical(component.get(key, u'')))
                    for key in keys)

        events.append(Event(rrule, **args))
    return events


def get_state_js(datadir):
    return os.path.join(datadir, 'state.js')


def load_state(datadir):
    path = get_state_js(datadir)
    if not os.path.exists(path):
        # save the state here so we can fail on permissions errors
        # before sending email.
        save_state(datadir, {})
        return {}

    return json.loads(open(path, 'rb').read())


def save_state(datadir, data):
    path = get_state_js(datadir)
    open(path, 'wb').write(json.dumps(data))


def handle_section(section, cfg):
    # TODO: These override default section defaults.
    # TODO: Handle absence of variables.
    icsfile = normalize_path(cfg.get(section, 'icsfile'))
    datadir = normalize_path(cfg.get(section, 'datadir'), DIR)
    remind = int(cfg.get(section, 'remind'))

    # TODO: catch exceptions with state loading here
    state = load_state(datadir)

    today = datetime.date.today()
    events = parse_ics(icsfile)
    for event in events:
        # TODO: Rewrite this to use rrule and .after(date, inc=True)
        delta = event.rrule - today
        if remind <= delta.days:
            print "REMIND ME!"


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
