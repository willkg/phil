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
import ConfigParser

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
    icsfile = normalize_path(cfg.get('default', 'icsfile'))
    remind = int(cfg.get('default', 'remind'))
    datadir = normalize_path(cfg.get('default', 'datadir'), DIR)
    host = cfg.get('default', 'smtp_host')
    if cfg.has_option('default', 'smtp_port'):
        port = int(cfg.get('default', 'smtp_port'))
    else:
        port = 25
    sender = cfg.get('default', 'from')
    to_list = cfg.get('default', 'to').splitlines()

    return Section(icsfile, remind, datadir, host, port, sender, to_list)


def handle_cfg(cfg, quiet, debug):
    if not quiet:
        out('Parsing config file....')
    try:
        section = parse_cfg(cfg)
    except ConfigParser.NoOptionError, noe:
        err('Missing option in config file: %s' % noe)
        return

    dtstart = datetime.datetime.today()

    # TODO: Catch exceptions with state loading here.
    if not quiet:
        out('Loading state....')

    state = load_state(section.datadir)

    if not quiet:
        out('Parsing ics file "%s"....' % section.icsfile)

    events = parse_ics(section.icsfile)
    for event in events:
        if not quiet:
            out('Looking at event "%s"....' % event.summary)

        next_date = get_next_date(dtstart, event.rrule)
        previous_remind = state.get(event.event_id)
        if previous_remind and previous_remind == str(next_date.date()):
            if not quiet:
                out('Already sent a reminder for this meeting.')
            continue

        if should_remind(dtstart, next_date, section.remind):
            if not quiet:
                out('Sending reminder....')
            summary = event.summary
            description = event.description

            if debug:
                out('From:', section.sender)
                out('To:', section.to_list)
                out('Subject:', summary)
                out('Body:')
                out(description)
            else:
                send_mail_smtp(section.sender, section.to_list, summary,
                               description, section.host, section.port)

            state[event.event_id] = str(next_date.date())
        else:
            if not quiet:
                out('Next reminder should get sent on %s.' %
                    (next_date.date() - datetime.timedelta(section.remind)))

    save_state(section.datadir, state)


def send_mail_smtp(from_name, from_addr, to_list, subject, body, host, port):
    server = smtplib.SMTP(host, port)

    for to_name, to_addr in to_list:
        msg = MIMEText(body)
        msg['To'] = email.utils.formataddr((from_name, from_addr))
        msg['From'] = email.utils.formataddr((to_name, to_addr))
        msg['Subject'] = subject
        server.sendmail(from_addr, [to_addr], msg.as_string())

    server.quit()


def check_for_events(conf, quiet, debug):
    cfg = parse_configuration(conf)

    try:
        handle_cfg(cfg, quiet, debug)

    except Exception:
        import traceback
        err(''.join(traceback.format_exc()), wrap=False)
        err('phil has died unexpectedly.  If you think this is an error '
            '(which it is), then contact phil\'s authors for help.')
        return 1

    if not quiet:
        out('Finished!')
    return 0
