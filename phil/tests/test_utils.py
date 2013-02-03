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


import os
from nose.tools import eq_, assert_raises
import datetime
import dateutil.rrule

from phil.tests import get_test_data_dir
from phil.util import (
    normalize_path, FILE, DIR, parse_ics, should_remind, get_next_date,
    FREQ_MAP)


def test_normalize_path():
    tests = (
        (__file__, FILE, __file__),
        (os.path.dirname(__file__), DIR, os.path.dirname(__file__))
        )

    for text, filetype, ret in tests:
        eq_(normalize_path(text, filetype), ret)

    failed_tests = (
        (None, FILE),  # None
        ('', FILE),  # empty string
        (__file__ + 'foo', FILE),  # non-existent file
        (__file__, DIR),  # file, but dir filetype
        (os.path.dirname(__file__), FILE),  # dir, but file filetype
        )

    for text, filetype in failed_tests:
        assert_raises(ValueError, normalize_path, text, filetype)


def test_parse_ics():
    test1 = os.path.join(get_test_data_dir(), 'test1.ics')
    events = parse_ics(test1)

    eq_(len(events), 1)

    ev = events[0]
    eq_(ev.event_id, u'2011-11-18 12:00:00+00:00::bi-weekly conference call::')
    eq_(ev.summary, u'bi-weekly conference call')
    eq_(ev.description, u'conference call')

    # TODO: Test with other ics files
    # TODO: Test multiple events


def test_ics_description_expansion():
    test2 = os.path.join(get_test_data_dir(), 'test2.ics')
    events = parse_ics(test2)

    eq_(len(events), 1)

    ev = events[0]
    eq_(ev.description,
        u'Weekly conference call\nLocation: IRC\nMeeting agenda and notes: '
        'http://example.com/notes/%(Y)s-%(m)s-%(d)s\n\nBe there or be '
        'square!')


def test_should_remind():
    def build_rrule(freq, **args):
        freq = FREQ_MAP[freq]
        return dateutil.rrule.rrule(freq, **args)

    # look at yesterday at 12:00
    today = datetime.datetime.today()
    td = datetime.timedelta

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
