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
import datetime
import fudge

from phil.tests import get_test_data_dir, TempFileTestCase
from phil.util import Config
from phil.check import Phil


class CheckTests(TempFileTestCase):
    @fudge.patch('datetime.datetime.today')
    @fudge.patch('phil.util')
    def test_check(self, faketoday, fakeutil):
        (faketoday
         .is_callable()
         .expects_call()
         .returns(
             datetime.datetime(2011, 12, 29, 22, 35, 44, 600000)
             )
         )

        (fakeutil
         .expects('load_state')
         .returns({})
         .expects('save_state')
         .expects('send_mail_smtp')
         .with_args(
             'sender@example.com', ['recip@example.com'],
             u'bi-weekly conference call (Fri December 30, 2011 00:00)',
             u'Weekly conference call\nLocation: IRC\nMeeting agenda '
             'and notes: http://example.com/notes/2011-12-30\n\nBe '
             'there or be square!',
             'localhost', 25)
         )

        test2_path = os.path.join(get_test_data_dir(), 'test2.ics')

        p = Phil(quiet=True, debug=False)
        p.config = Config(test2_path, 3, self.tempdir, 'localhost', 25,
                          'sender@example.com', ['recip@example.com'])
        p._run()
