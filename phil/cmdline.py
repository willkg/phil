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

import argparse
import sys
import os


try:
    import phil
except ImportError:
    sys.stderr.write(
        'The phil library is not on your sys.path.  Please install phil.\n')
    sys.exit(1)


BYLINE = ('phil-cmd: {0} ({1}).  Licensed under the GPLv3.'.format(
        phil.__version__, phil.__releasedate__))
USAGE = 'Usage: phil [program-options] COMMAND [command-options] ARGS'
DESC = """
Command line interface for phil.
"""


def createfile_cmd(parsed):
    outfile = parsed.conffile
    path = os.path.abspath(outfile)
    conffile = phil.get_template()
    if os.path.exists(path):
        phil.err('{0} exists.  Remove it and try again or try again with '
                 'a different filename.'.format(outfile))
        return 1

    f = open(path, 'w')
    f.write(conffile)
    f.close()

    phil.out('{0} written.  Open it in your favorite editor and read it.'
        .format(outfile))
    return 0


def run_cmd(parsed):
    conffile = os.path.abspath(parsed.runconffile)
    if not os.path.exists(conffile):
        phil.err('{0} does not exist.'.format(conffile))
        return 1

    p = phil.Phil(parsed.quiet, parsed.debug)
    return p.run(conffile)


def next6_cmd(parsed):
    conffile = os.path.abspath(parsed.runconffile)
    if not os.path.exists(conffile):
        phil.err('{0} does not exist.'.format(conffile))
        return 1

    p = phil.Phil(parsed.quiet, parsed.debug)
    return p.next6(conffile)


def main(argv):
    if '-q' not in argv and '--quiet' not in argv:
        phil.out(BYLINE)

    parser = argparse.ArgumentParser(
        description=phil.wrap_paragraphs(
            'phil allows you to set up email reminders for meetings.'
            '\n\n'
            'This program comes with ABSOLUTELY NO WARRANTY.  '
            'This is free software and you are welcome to redistribute it'
            'under the terms of the GPLv3.'),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        default=False,
        help='runs phil quietly--only prints errors')

    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='runs phil in debug mode--no sending email.')

    subparsers = parser.add_subparsers(
        title='Commands',
        help='Run "%(prog)s CMD --help" for additional help')

    createfile_parser = subparsers.add_parser(
        'createfile', help='rreates a configuration file')
    createfile_parser.add_argument(
        'conffile',
        help='name/path for the configuration file')
    createfile_parser.set_defaults(func=createfile_cmd)

    run_parser = subparsers.add_parser(
        'run', help='runs phil on the given configuration file')
    run_parser.add_argument(
        'runconffile',
        help='name/path for the configuration file')
    run_parser.set_defaults(func=run_cmd)

    next6_parser = subparsers.add_parser(
        'next6', help='tells you next 6 dates for an event')
    next6_parser.add_argument(
        'runconffile',
        help='name/path for the configuration file')
    next6_parser.set_defaults(func=next6_cmd)

    parsed = parser.parse_args(argv)

    return parsed.func(parsed)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
