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

from phil.check import parse_ics
from phil.tests import get_test_data_dir


def test_parse_ics():
    test1 = os.path.join(get_test_data_dir(), 'test1.ics')
    events = parse_ics(test1)

    eq_(len(events), 1)

    ev = events[0]
    eq_(ev.summary, u'bi-weekly conference call')
    eq_(ev.description, u'conference call')
    eq_(ev.organizer, u'')
    eq_(ev.url, u'')
    
    # TODO: test with other ics files
