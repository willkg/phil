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
import tempfile
import unittest
import shutil
import ConfigParser


class TempFileTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tempdir)


def build_config(section, icsfile, datadir, remind):
    cfg = ConfigParser.SafeConfigParser()
    cfg.add_section(section)
    cfg.set(section, 'icsfile', icsfile)
    cfg.set(section, 'datadir', datadir)
    cfg.set(section, 'remind', remind)


def get_test_data_dir():
    return os.path.join(os.path.dirname(__file__), 'testdata')
