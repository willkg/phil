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


from collections import namedtuple

import datetime
import dateutil.rrule

from phil.configuration import parse_configuration
from phil.util import out, err, normalize_path, DIR, load_state, save_state
from icalendar import Calendar, vDatetime, vText

import smtplib
import email.utils
from email.mime.text import MIMEText


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
    def tweak(rrule, key):
        value = rrule.get(key)
        if isinstance(value, list):
            return value[0]
        return value
    args = dict((key, tweak(rrule, key)) for key in keys)
    return freq, args


Event = namedtuple('Event', ['event_id', 'rrule', 'summary', 'description'])


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

        summary = vText.from_ical(component.get('summary', u''))
        description = vText.from_ical(component.get('description', u''))
        organizer = vText.from_ical(component.get('organizer', u''))

        # TODO: Find an event id.  If it's not there, then compose one
        # with dtstart, summary, and organizer.
        event_id = "::".join((str(dtstart), summary, organizer))

        events.append(Event(event_id, rrule, summary, description))
    return events


def get_next_date(dtstart, rrule):
    return rrule.after(dtstart, inc=True)


def should_remind(dtstart, next_date, remind):
    delta = next_date.date() - dtstart.date()
    return remind == delta.days


Section = namedtuple('Section', ['icsfile', 'remind', 'datadir', 'host',
                                 'port', 'sender', 'to_list'])


def parse_cfg(cfg):
    def extract_or_fail(key, type_):
        value = cfg.get('default', key)
        if value is None:
            raise ValueError('%s is not defined.')

        return type_(value)

    icsfile = normalize_path(extract_or_fail('icsfile', str))
    remind = extract_or_fail('remind', int)
    datadir = normalize_path(extract_or_fail('datadir', str), DIR)
    host = extract_or_fail('smtp_host', str)
    port = int(cfg.get('default', 'smtp_port', 25))
    sender = extract_or_fail('from', str)
    to_list = extract_or_fail('to', str).splitlines()

    return Section(icsfile, remind, datadir, host, port, sender, to_list)


def handle_cfg(cfg):
    section = parse_cfg(cfg)
    dtstart = datetime.datetime.today()

    # TODO: Catch exceptions with state loading here.
    state = load_state(section.datadir)

    events = parse_ics(section.icsfile)
    for event in events:
        next_date = get_next_date(dtstart, event.rrule)
        previous_remind = state.get(event.event_id)
        if previous_remind:
            if previous_remind == str(next_date.date()):
                continue

        if should_remind(dtstart, next_date, section.remind):
            summary = event.summary
            description = event.description

            send_mail_smtp(section.sender, section.to_list, summary,
                           description, section.host, section.port)

        state[event.event_id] = str(next_date.date())

    save_state(section.datadir, state)


def check_for_events(conf, quiet, debug):
    cfg = parse_configuration(conf)

    try:
        handle_cfg(cfg)

    except Exception, e:
        import traceback
        err(''.join(traceback.format_exc()))
        err('%s (%r)' % (e, e))
        return 1

    if not quiet:
        out('done!')
    return 0


def send_mail_smtp(from_name, from_addr, to_list, subject, body, host, port):
    server = smtplib.SMTP(host, port)

    for to_name, to_addr in to_list:
        msg = MIMEText(body)
        msg['To'] = email.utils.formataddr((from_name, from_addr))
        msg['From'] = email.utils.formataddr((to_name, to_addr))
        msg['Subject'] = subject
        server.sendmail(from_addr, [to_addr], msg.as_string())

    server.quit()
