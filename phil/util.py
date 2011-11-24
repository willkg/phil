#######################################################################
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
import textwrap
import sys
import json


FILE = 'file'
DIR = 'dir'


def normalize_path(path, filetype=FILE):
    """Takes a path and a filetype, verifies existence and type, and
    returns absolute path.

    """
    if not path:
        raise ValueError('"%s" is not a valid path.' % path)
    if not os.path.exists(path):
        raise ValueError('"%s" does not exist.' % path)
    if filetype == FILE and not os.path.isfile(path):
        raise ValueError('"%s" is not a file.' % path)
    elif filetype == DIR and not os.path.isdir(path):
        raise ValueError('"%s" is not a dir.' % path)

    return os.path.abspath(path)


def wrap_paragraphs(text):
    text = ['\n'.join(textwrap.wrap(mem)) for mem in text.split('\n\n')]
    return '\n\n'.join(text)


def err(*output):
    output = '\n'.join(textwrap.wrap(' '.join(output)))
    sys.stderr.write(output + '\n')


def out(*output):
    output = '\n'.join(textwrap.wrap(' '.join(output)))
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
