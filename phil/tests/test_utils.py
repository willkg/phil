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
from nose.tools import eq_, assert_raises


def test_normalize_path():
    from phil.util import normalize_path, FILE, DIR

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
