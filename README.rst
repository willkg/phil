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

    Will sets up phil and runs it in a cron job that kicks off every morning,
    checks the iCalendar files, and sends out meeting reminders accordingly.

.. _iCalendar: http://tools.ietf.org/html/rfc5545


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


Install
=======

To install phil, do::

    pip install phil


Configure
=========

phil requires a configuration file.  To generate a sample configuration file
run phil this way::

    phil-cmd createfile [configfile]

Go through the file.  It is self-documenting.


Run
===

For help, do this::

    phil-cmd --help


To run phil, do this::

    phil-cmd run <configfile>

This runs phil with the given config file.


Resources
=========

http://tools.ietf.org/html/rfc5545#section-3.8.5.3

http://labix.org/python-dateutil

http://pypi.python.org/pypi/icalendar/3.0
