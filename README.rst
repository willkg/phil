======
 phil
======

Summary
=======

phil is a command line utility that sends reminder emails about meetings
as defined in an `iCalendar`_ file.

It solves this use case:

    Will works on a project that has meetings every saturday.  Will wants
    an automated way to send a reminder email to everyone about the meeting
    with the details of when the meeting is, how to attend, and where
    the notes for the meeting will be.

    Will installs and configures phil to send emails to the project list 
    before the saturday meetings.  Will sets up a cron job to kick phil off
    every morning to check for reminders it needs to send and send them.

.. _iCalendar: http://tools.ietf.org/html/rfc5545


Features
========

* has a configuration file in config.ini format
* parses iCalendar files, calculates the next valid meeting date, and sends
  reminder email x days before the meeting
* tries not to remind you about the same meeting twice!
* has a ``--debug`` mode allowing you to test things without actually sending
  email
* has a ``--quiet`` mode that will only print errors
* correctly prints errors to stderr and output to stdout; also returns error
  code 1 if it failed
* show the next 6 dates for an event with the ``next6`` command


History
=======

I work on a bunch of projects some of which have regular meetings.  One day
I realized that it would help a lot if I had some automated way to send out
meeting reminders to everyone with some text that specified when the meeting
was, how to attend the meeting, and where to look for details on what the
meeting will cover.

I work on a bunch of projects and have a hell of a time coming up with
good names for them all.  I don't really remember the names of libraries
and things I use, so I figure arbitrary names are fine so long as there is
sufficient documentation that allows search engines to find the project
given search criteria.  Given that, I decided to name all my projects going
forward with names like phil.

Thus phil was born.


License, etc
============

phil Copyright(C) 2011, 2013 Will Kahn-Greene

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.  See
the Terms and Conditions section of `LICENSE`_ for details.

.. _LICENSE: http://www.gnu.org/licenses/gpl-3.0.html


Install
=======

If you want a released version of phil, do this::

    $ pip install phil


If you want a bleeding edge version of phil, do this::

    $ git clone git://github.com/willkg/phil.git
    $ cd phil
    $ python setup.py install


Configure
=========

phil requires a configuration file.  To generate a sample configuration file
run phil this way::

    phil-cmd createfile <configfile>

The config file is self-documenting.  Go through it to configure phil.

.. Note::

   If you want to keep a pristine example config file with the documentation,
   run ``phil-cmd createfile config_pristine.ini``.


Run
===

For list of subcommands, arguments and other help, do this::

    phil-cmd --help


To email reminders for meetings, do this::

    phil-cmd run <configfile>

This runs phil with the given config file.

phil has a quiet mode which only prints errors::

    phil-cmd --quiet ...


phil has a debug mode which does everything **except** actually send email::

    phil-cmd --debug ...


phil keeps track of the last meeting date/time that it reminded you about.
If you run phil twice, it'll only remind you about a meeting once.


Test
====

phil comes with unit tests.  Unit tests are executed using `nose`_ and
use `fudge`_ as a mocking framework.  If you don't already have nose
and fudge installed, then install them with::

    pip install nose fudge

I like to use `nose-progressive`_, too, because it's awesome.  To
install that::

    pip install nose-progressive

To run the unit tests from a git clone or the source tarball, do this
from the project directory::

    nosetests

With nose-progressive and fail-fast::

    nosetests -x --with-progressive


.. _nose-progressive: http://pypi.python.org/pypi/nose-progressive/
.. _nose: http://code.google.com/p/python-nose/
.. _fudge: http://farmdev.com/projects/fudge/


Source code
===========

Source code is hosted on github.

https://github.com/willkg/phil


Issue tracker
=============

Issue tracker is hosted on github.

https://github.com/willkg/phil/issues


Resources I found helpful
=========================

* http://tools.ietf.org/html/rfc5545#section-3.8.5.3
* http://labix.org/python-dateutil
* http://pypi.python.org/pypi/icalendar/3.0
