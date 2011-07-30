#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2011 Thomas Schreiber
#
# Developed by Thomas Schreiber <ubiquill@gmail.com>
#
# Contributors:
#    Greg Haynes
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
from setuptools import setup, find_packages

setup(
    name = "potluck",
    version = "0.1",
    author = "Thomas Schreiber",
    author_email = "ubiquill@gmail.com",
    description = ("PyQt frontend to Archlinux's Pacman and the AUR"),
    license = "GPL v2",
    keywords = "pyqt pacman aur package",
    url = "http://ubiquill.github.com/potluck",
    packages = find_packages(),
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    classifiers = [
        "Development Status :: 1 - Beta",
        "Topic :: Utilities",
        "Environment :: X11 Application :: Qt",
        "Intended Audience :: New Arch Users",
        "Programming Language :: Python :: 3",
        "Topic :: Package Management :: GUI",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    include_package_data = True,
    package_data = {'src':['potluck', 'view/icons/*', 'view/*.ui', 'view/*.qrc', 'model/*.sh', 'model/scripts/*'],'':['COPYING', 'README']},
)                          

# vim: set ts=4 sw=4 noet:
