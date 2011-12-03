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
from nose.tools import eq_
import datetime
import dateutil.rrule

from phil.check import parse_ics, should_remind, get_next_date, FREQ_MAP
from phil.tests import get_test_data_dir


def test_parse_ics():
    test1 = os.path.join(get_test_data_dir(), 'test1.ics')
    events = parse_ics(test1)

    eq_(len(events), 1)

    ev = events[0]
    eq_(ev.event_id, u'2011-11-18 12:00:00::bi-weekly conference call::')
    eq_(ev.summary, u'bi-weekly conference call')
    eq_(ev.description, u'conference call')
    
    # TODO: Test with other ics files
    # TODO: Test multiple events


def test_should_remind():
    def build_rrule(freq, **args):
        freq = FREQ_MAP[freq]
        return dateutil.rrule.rrule(freq, **args)

    # look at yesterday at 12:00
    today = datetime.datetime.today()
    td = datetime.timedelta

    # 0 days from now
    rule = build_rrule('DAILY', dtstart=today, interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 1 days from now
    rule = build_rrule('DAILY', dtstart=today + td(1), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), True)

    # 2 day from now
    rule = build_rrule('DAILY', dtstart=today + td(2), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 3 days from now
    rule = build_rrule('DAILY', dtstart=today + td(3), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 4 days from now
    rule = build_rrule('DAILY', dtstart=today + td(4), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 5 days from now
    rule = build_rrule('DAILY', dtstart=today + td(5), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 6 days from now
    rule = build_rrule('DAILY', dtstart=today + td(6), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 1), False)

    # 3 days from now, remind in 3
    rule = build_rrule('DAILY', dtstart=today + td(3), interval=7)
    eq_(should_remind(today, get_next_date(today, rule), 3), True)
