# -*- coding: utf-8 -*-
"""

tools.py
-----------

This module provides several handy tools to avoid some repetative work and
to fancy-fy some of the output made by mmacman/pyalpmm
"""

import time
import sys, os
import math
from functools import update_wrapper
from operator import le, lt, eq, ne, ge, gt
import pyalpmm_raw as p

def CachedProperty(method):
    """A decorator which implements an advanced Property, which executes the
    body of the decorated method just once and caches the result inside
    the .

    :param method: the decorated method
    """
    name = method.__name__
    def _get(self):
        return self.__dict__.setdefault(name, method(self))
    update_wrapper(_get, method)

    def _del(self):
        self.__dict__ .pop(name, None)
    return property(_get, None, _del)


class ProgressBar(object):
    """This is a Quick-Shot on a ProgressBar to make `mmacman` a little
    more charming.

    :param endvalue: final value means 100percent as int (optional)
    :param label: a describing label (optional)
    :param length: set this to a positive int to get a fixed size bar (optional)
    """
    template = {
        "left"      : "[<",
        "mid"       : "_",
        "right"     : ">]",
        "perc"      : "{0:>6.1f}%",
        "fill"      : "#"
    }
    prefix = "[i] "
    pad_right = 0

    def __init__(self, endvalue=None, label=None):
        self.endvalue = endvalue
        self.label = label or ""
        self.percent = 0
        self.tick = 0
        self.last_step = time.time() - 20
        self.last_sleep = 0.020

    def _get_bar(self, filled):
        """Return the :class:`ProgressBar` directly ready to write it on the
        screen. Oh no, I mean - ah whateva. Naming of all the spacing and stuff
        is done like that:

        |---------------- window width(self.max_width) ------------------|
        |<prefix><label><space_left><full_bar_width><perc><right_space>  |

        :param filled: the number of chars filled with the "fill" char
        """
        empty = self.bar_width - filled
        self.tick += 1

        t = self.template
        if self.endvalue is None:
            mid = t["fill"] * filled
            if empty == 0:
                left_empty, right_empty = "", ""
            else:
                left_empty = t["mid"] * (empty - self.tick % empty)
                right_empty = t["mid"] * (self.tick % empty)

            if self.label is None:
                # get a endless, unlabled progressbar
                return t["left"] + left_empty + mid + right_empty + t["right"]
            # get a endless, labeled progressbar
            return "{0:{1}}{2}".format(
                self.label,
                self.space_left,
                t["left"] + left_empty + mid + right_empty + t["right"]
            )
        elif self.endvalue:
            fill, mid = t["fill"] * filled, t["mid"] * empty
            if self.label:
                # get a deterministic, un-labeled progressbar
                return "{0:{1}}{2}{3}".format(
                    self.label,
                    self.space_left,
                    t["left"] + fill + mid + t["right"],
                    t["perc"].format(self.percent)
                )
            # get a deterministic, labeled progressbar
            return "{0}{1}".format(
                t["left"] + fill + mid + t["right"],
                t["perc"].format(self.percent)
            )

    def step_to(self, value):
        """This is the method called from outside to feed the
        :class:`ProgressBar` instance with new data. Also the process is sent
        to sleep for some ms, but guess what: i don't think thats the right way
        to lower the cputime needed by the process without sleep.

        :param value: the now reached value
        """
        # dynamicly optimize the sleep duration for maximal speed
        time.sleep(self.last_sleep)
        self.last_sleep = int(self.last_sleep*0.5) \
            if (time.time() - self.last_step < self.last_sleep*1.1) else \
            int(self.last_sleep*1.3)
        self.last_step = time.time()

        if self.endvalue:
            self.percent = min((value / (self.endvalue/100.)), 100)
            filled = int(math.ceil((self.bar_width/100.) * self.percent))
        else:
            filled = min(self.bar_width, value)

        return self._get_bar(filled)

    def step_to_end(self):
        """Should be called before jumping to the next line in order to have a
        nice optical clean progressbar
        """
        self.percent = 100
        filled = self.bar_width
        return self._get_bar(filled)

    @property
    def max_width(self):
        """Maximum available width in this console window"""
        return int(os.popen('stty size', 'r').read().split()[1]) - 3

    @property
    def bar_width(self):
        """Width of the dynamic part of the progressbar"""
        if self.max_width < 80:
            return 30
        return int((self.max_width - 45) * 0.8)

    @property
    def full_bar_width(self):
        """Full width of the progressbar including frame-chars"""
        return self.bar_width + \
               len(self.template["left"]) + \
               len(self.template["right"])

    @property
    def space_left(self):
        """This is the spacing used left of the whole bar"""
        return self.max_width - self.full_bar_width - \
               self.pad_right - \
               (len(self.template["perc"].format(100)) \
                if self.endvalue else 0)


class AskUser(object):
    """Ask the user on the console - can be answered only with the given
    possibilities - save the valid, entered value in :attr:`self.answer`

    :param question: the question the user should be asked
    :param ansers: a list of possible answers (case-insensitive)
    """
    def __init__(self, question, answers=["y","n"]):
        ans = ""
        while not ans.lower() in answers:
            sys.stdout.write(question)
            sys.stdout.flush()
            self.answer = ans = raw_input().lower()


class FancyOutput(object):
    """A baseclass for a container to easily output data in a friendly readable
    formatting, but also keep the original data for later use.

    :param data: the raw data to fancyfy
    """
    def __init__(self, data):
        self.raw = data
        self.out = data

    def rebuild(self, **kw):
        return self.__class__(self.raw, **kw)

    def __len__(self):
        return len(self.out)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.raw == self.raw
        return self.raw == other

    __unicode__ = __repr__ = __str__ = lambda s: str(s.out)

class FancySize(FancyOutput):
    """Nicely format filesizes in B, kB, MB and GB suffixes"""

    suffixes = {"B":1. ,"kB": 1024., "MB": 1024*1024., "GB": 1024*1024*1024.}

    def __init__(self, bytes, force_suffix=None):
        self.raw = b = self.out = long(bytes)
        self.force_suffix = force_suffix

        if force_suffix in self.suffixes:
            label, divider = force_suffix, self.suffixes[force_suffix]
            self.out = "{0:.1f} {1}".format(b/divider, label)

        else:
            for label, divider in self.suffixes.items():
                if 1 <= (b / divider) < 1024:
                    self.out = "{0:.1f} {1}".format(b/divider, label)
                    break

class FancyFileConflictType(FancyOutput):
    """Human readable represantation of the file conflict types"""
    def __init__(self, data):
        self.raw = d = data
        if self.raw == p.PM_FILECONFLICT_TARGET:
            self.out = "detected file in two packages"
        elif self.raw == p.PM_FILECONFLICT_FILESYSTEM:
            self.out = "detected file in filesystem"

class FancyDateTime(FancyOutput):
    """A ASCTime representation of a DateTime"""
    def __init__(self, data):
        if data == 0:
            self.raw = self.tup = self.out = ""
        else:
            self.raw = d = data
            self.tup = time.gmtime(d)
            self.out = time.asctime(self.tup)

class FancyReason(FancyOutput):
    """Human readable representation of the reason why a package was installed
    """
    def __init__(self, data):
        self.raw = data
        self.out = \
            {p.PM_PKG_REASON_EXPLICIT: "explicitly requested by the user",
             p.PM_PKG_REASON_DEPEND: "installed as a dependency"}[data]

class FancyPackage(FancyOutput):
    """Show all available PackageItem attributes (means: those with a None value
    won't be showed) in a more or less fancy table-like layout.
    """
    def __init__(self, pkg):
        from pyalpmm.lists import LazyList

        o = "<### Package Info:\n"
        for key, val in ((x, pkg.get_info(x)) for x in pkg.all_attributes):
            if not val:
                continue
            elif isinstance(val, LazyList):
                o += "%13s - %s\n" % (key, val) if len(val) < 8 \
                    else "%13s - | list too long - size:%s |  \n" % (
                    key, len(val))
            else:
                o += "%13s - %s\n" % (key, val)
        o += "###>"
        self.raw = pkg
        self.out = o

class FancyVersion(FancyOutput):
    """Provide a convenient way to store and compare different version labels"""
    def __init__(self, version):
        self.raw = d = version
        self.data = version.split(".") if "." in version else d
        #d = sum([sub_version.split("-") for sub_version in d], [])

        self.out = self.raw

    def _general_compare(self, other, operator):
        if isinstance(other, str):
            return operator(self.raw, other)
        elif not isinstance(other, FancyVersion):
            raise TypeError("You can only compare a FancyVersion "
                            "against another FancyVersion")
        for i in range(min(len(other.data), len(self.data))):
            if operator(self.data[i], other.data[i]):
                return True
        return False
    def __lt__(self, other):
        return self._general_compare(other, lt)
    def __le__(self, other):
        return self._general_compare(other, le)
    def __gt__(self, other):
        return self._general_compare(other, gt)
    def __ge__(self, other):
        return self._general_compare(other, ge)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __eq__(self, other):
        if isinstance(other, str):
            return self.raw == other
        elif not isinstance(other, FancyVersion):
            raise TypeError("You can only compare a FancyVersion "
                            "against another FancyVersion")
        if self.raw == other.raw:
            return True
        return False


class CriticalError(Exception):
    def __init__(self, msg):
        super(CriticalError, self).__init__(msg)

    def format(self, *v, **kw):
        """Implement our own :meth:`self.format` so we can easily propagade
        errors from bottom to top and alter their content on their way up

        :param v: the positional arguments to pass as format arguments
        :param kw: the keyword arguments to pass as format arguments
        """
        self.args = tuple(
            arg.format(*v, **kw) for arg in self.args if isinstance(arg, str)
        )

class UserError(Exception):
    pass
