######################################################################
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


import ConfigParser
import datetime

import phil.util
from phil.util import (
    out, err, parse_configuration, parse_ics, get_next_date, should_remind,
    format_date, generate_date_bits)


class Phil(object):
    def __init__(self, quiet=False, debug=False):
        self.config = None
        self.quiet = quiet
        self.debug = debug

    def _run(self):
        dtstart = datetime.datetime.today()

        if not self.quiet:
            out('Loading state....')

        state = phil.util.load_state(self.config.datadir)

        if not self.quiet:
            out('Parsing ics file "{0}"....'.format(self.config.icsfile))

        events = parse_ics(self.config.icsfile)
        for event in events:
            if not self.quiet:
                out('Looking at event "{0}"....'.format(event.summary))

            next_date = get_next_date(dtstart, event.rrule)
            previous_remind = state.get(event.event_id)
            if previous_remind and previous_remind == str(next_date.date()):
                if not self.quiet:
                    out('Already sent a reminder for this meeting.')
                continue

            if should_remind(dtstart, next_date, self.config.remind):
                if not self.quiet:
                    out('Sending reminder....')
                summary = '{0} ({1})'.format(
                    event.summary, format_date(next_date))
                description = event.description % generate_date_bits(next_date)

                if self.debug:
                    out('From:', self.config.sender)
                    out('To:', self.config.to_list)
                    out('Subject:', summary)
                    out('Body:')
                    out(description, indent='    ', wrap=False)
                else:
                    phil.util.send_mail_smtp(
                        self.config.sender, self.config.to_list, summary,
                        description, self.config.host, self.config.port)

                    state[event.event_id] = str(next_date.date())
            elif not self.quiet:
                out('Next reminder should get sent on {0}.'.format(
                    next_date.date() - datetime.timedelta(self.config.remind)))

        phil.util.save_state(self.config.datadir, state)

    def run(self, conffile):
        if not self.quiet:
            out('Parsing config file....')
        try:
            self.config = parse_configuration(conffile)
        except ConfigParser.NoOptionError, noe:
            err('Missing option in config file: {0}'.format(noe))
            return 1

        try:
            self._run()

        except Exception:
            import traceback
            err(''.join(traceback.format_exc()), wrap=False)
            err('phil has died unexpectedly.  If you think this is an error '
                '(which it is), then contact phil\'s authors for help.')
            return 1

        if not self.quiet:
            out('Finished!')
        return 0

    def _next6(self):
        # TODO: This is a repeat of _run for the most part.
        dtstart = datetime.datetime.today()

        out('Loading state....')

        state = phil.util.load_state(self.config.datadir)

        out('Parsing ics file "{0}"....'.format(self.config.icsfile))

        events = parse_ics(self.config.icsfile)
        for event in events:
            out('Looking at event "{0}"....'.format(event.summary))
            next_date = dtstart

            for i in range(6):
                next_date = get_next_date(next_date, event.rrule)
                previous_remind = state.get(event.event_id)
                if (previous_remind
                        and previous_remind == str(next_date.date())):
                    out('* {0} (sent reminder already)'.format(
                        next_date.strftime('%c')))

                else:
                    out('* {0}'.format(next_date.strftime('%c')))

                next_date = next_date + datetime.timedelta(1)

    def next6(self, conffile):
        if not self.quiet:
            out('Parsing config file....')
        try:
            self.config = parse_configuration(conffile)
        except ConfigParser.NoOptionError, noe:
            err('Missing option in config file: {0}'.format(noe))
            return 1

        try:
            self._next6()

        except Exception:
            import traceback
            err(''.join(traceback.format_exc()), wrap=False)
            err('phil has died unexpectedly.  If you think this is an error '
                '(which it is), then contact phil\'s authors for help.')
            return 1

        if not self.quiet:
            out('Finished!')
        return 0
