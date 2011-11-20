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

phil Copyright(C) 2011 Will Kahn-GReene

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.  See
the Terms and Conditions section of `LICENSE`_ for details.

.. _LICENSE: http://www.gnu.org/licenses/gpl-3.0.html


Install
=======

phil hasn't been released, yet.  Once it's released, you can install it with
pip.  Until then, you can:

1. ``git clone git://github.com/willkg/phil.git``
2. ``cd phil``
3. ``python setup.py install``


Configure
=========

phil requires a configuration file.  To generate a sample configuration file
run phil this way::

    phil-cmd createfile <configfile>

The config file is self-documenting.  Go through it to configure phil.

.. Note::

   If you want to keep a pristine example config file with the documentation,
   run ``phil-cmd createfile <configfile>`` and copy the resulting file to
   another name.


Run
===

For help, do this::

    phil-cmd --help


To email reminders for meetings, do this::

    phil-cmd run <configfile>

This runs phil with the given config file.


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
