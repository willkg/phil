#######################################################################
# This file is part of phil.
#
# Copyright (C) 2011, 2012, 2013 Will Kahn-Greene
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
import textwrap
import sys
import json
import ConfigParser
from icalendar import Calendar, vDatetime, vDDDTypes, vText
import dateutil.rrule
from collections import namedtuple
import smtplib
import email.utils
from email.mime.text import MIMEText


FILE = 'file'
DIR = 'dir'


def format_date(date):
    return date.strftime('%a %B %d, %Y %H:%M')


def generate_date_bits(date):
    return dict((m, date.strftime('%' + m))
                for m in ('a', 'A', 'b', 'B', 'c', 'd', 'H', 'I', 'j',
                          'm', 'M', 'p', 'S', 'U', 'v', 'W', 'x', 'X',
                          'y', 'Y', 'Z'))


def normalize_path(path, filetype=FILE):
    """Takes a path and a filetype, verifies existence and type, and
    returns absolute path.

    """
    if not path:
        raise ValueError('"{0}" is not a valid path.'.format(path))
    if not os.path.exists(path):
        raise ValueError('"{0}" does not exist.'.format(path))
    if filetype == FILE and not os.path.isfile(path):
        raise ValueError('"{0}" is not a file.'.format(path))
    elif filetype == DIR and not os.path.isdir(path):
        raise ValueError('"{0}" is not a dir.'.format(path))

    return os.path.abspath(path)


def wrap(text, indent=''):
    return (
        textwrap.TextWrapper(initial_indent=indent, subsequent_indent=indent)
        .wrap(text))


def wrap_paragraphs(text):
    text = ['\n'.join(textwrap.wrap(mem)) for mem in text.split('\n\n')]
    return '\n\n'.join(text)


def err(*output, **kwargs):
    """Writes output to stderr.

    :arg wrap: If you set ``wrap=False``, then ``err`` won't textwrap
        the output.

    """
    output = 'Error: ' + ' '.join([str(o) for o in output])
    if kwargs.get('wrap') is not False:
        output = '\n'.join(wrap(output, kwargs.get('indent', '')))
    elif kwargs.get('indent'):
        indent = kwargs['indent']
        output = indent + ('\n' + indent).join(output.splitlines())
    sys.stderr.write(output + '\n')


def out(*output, **kwargs):
    """Writes output to stdout.

    :arg wrap: If you set ``wrap=False``, then ``out`` won't textwrap
        the output.

    """
    output = ' '.join([str(o) for o in output])
    if kwargs.get('wrap') is not False:
        output = '\n'.join(wrap(output, kwargs.get('indent', '')))
    elif kwargs.get('indent'):
        indent = kwargs['indent']
        output = indent + ('\n' + indent).join(output.splitlines())
    sys.stdout.write(output + '\n')


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


def ParseException(Exception):
    pass


def get_template():
    path = os.path.join(
        os.path.dirname(__file__), 'templates', 'config.ini')
    f = open(path, 'r')
    data = f.read()
    f.close()

    return data


Config = namedtuple('Config', ['icsfile', 'remind', 'datadir', 'host',
                               'port', 'sender', 'to_list'])


def parse_configuration(conffile):
    cfg = ConfigParser.SafeConfigParser()
    cfg.readfp(open(conffile))

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

    return Config(icsfile, remind, datadir, host, port, sender, to_list)


Event = namedtuple('Event', ['event_id', 'rrule', 'summary', 'description'])


FREQ_MAP = {
    # TODO: Make sure this covers all of them.
    'HOURLY': dateutil.rrule.HOURLY,
    'DAILY': dateutil.rrule.DAILY,
    'MONTHLY': dateutil.rrule.MONTHLY,
    'YEARLY': dateutil.rrule.YEARLY
    }


WEEKDAY_MAP = {
    # TODO: Make sure this covers all of them.
    'SU': dateutil.rrule.SU,
    'MO': dateutil.rrule.MO,
    'TU': dateutil.rrule.TU,
    'WE': dateutil.rrule.WE,
    'TH': dateutil.rrule.TH,
    'FR': dateutil.rrule.FR,
    'SA': dateutil.rrule.SA
    }


def get_next_date(dtstart, rrule):
    return rrule.after(dtstart, inc=True)


def should_remind(dtstart, next_date, remind):
    delta = next_date.date() - dtstart.date()
    return remind >= delta.days


def convert_rrule(rrule):
    """Converts icalendar rrule to dateutil rrule."""
    args = {}

    # TODO: rrule['freq'] is a list, but I'm unclear as to why.
    freq = FREQ_MAP[rrule['freq'][0]]

    keys = ['wkst', 'until', 'bysetpos', 'interval',
            'bymonth', 'bymonthday', 'byyearday', 'byweekno',
            'byhour', 'byminute', 'bysecond']

    def tweak(rrule, key):
        value = rrule.get(key)
        if isinstance(value, list):
            return value[0]
        return value

    args = dict((key, tweak(rrule, key)) for key in keys if rrule.get(key))

    byweekday = rrule.get('byweekday')
    if byweekday:
        byweekday = byweekday[0]
        count, day = int(byweekday[0]), byweekday[1:]
        args['byweekday'] = WEEKDAY_MAP[day](count)

    return freq, args


def parse_ics(icsfile):
    """Takes an icsfilename, parses it, and returns Events."""
    events = []

    cal = Calendar.from_ical(open(icsfile, 'rb').read())
    for component in cal.walk('vevent'):
        dtstart = component['dtstart'].dt
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


def send_mail_smtp(sender, to_list, subject, body, host, port):
    server = smtplib.SMTP(host, port)

    sender_name, sender_addr = email.utils.parseaddr(sender)
    to_list = [email.utils.parseaddr(addr) for addr in to_list]

    for to_name, to_addr in to_list:
        msg = MIMEText(body)
        msg['To'] = email.utils.formataddr((to_name, to_addr))
        msg['From'] = email.utils.formataddr((sender_name, sender_addr))
        msg['Subject'] = subject
        server.sendmail(sender_addr, [to_addr], msg.as_string())

    server.quit()
