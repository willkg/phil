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

from setuptools import setup, find_packages
import re
import os


READMEFILE = "README.rst"
VERSIONFILE = os.path.join("phil", "_version.py")
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"


def get_version():
    verstrline = open(VERSIONFILE, "rt").read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % VERSIONFILE)


setup(
    name="phil",
    version=get_version(),
    description="Sends email reminders for events in an iCalendar file",
    long_description=open(READMEFILE).read(),
    license="GPL",
    author="Will Kahn-Greene",
    author_email="willg@bluesock.org",
    keywords="phil icalendar rrule email",
    url="http://github.com/willkg/phil",
    zip_safe=True,
    packages=find_packages(),
    scripts=['scripts/phil-cmd'],
    install_requires=[
        "argparse",
        "icalendar",
        "python-dateutil==1.5",  # 2.0 and higher are for python3
        ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Communications :: Email",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    )
