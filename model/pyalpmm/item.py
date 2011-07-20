# -*- coding: utf-8 -*-
"""

item.py
-----------

This module is the interface between the C and the Python world, it describes
smart objects, which map to data, that is held in C space and can be simply
accessed through an attribute of the object with a quiet lazy evaluation.
"""

import os, sys
import heapq
from itertools import chain

import pyalpmm_raw as p

import lists as List
from tools import FancySize, FancyDateTime, FancyReason, FancyFileConflictType,\
     FancyVersion


class AbstractItem(object):
    """The baseclass for all *Item classes. Transalates Python attribute access
    on this object to the appropriate C function call. Also handles the mapping
    of the C types to Python types and vice versa.

    Each derived class may set one or more of the following class attributes to
    control the behaviour of the "translator".

    - attributes: a list of str, which will be translated. They directly map
                  to a (including a prefix) equally called C function.
    - ctype: name of the C type this class maps to
    - extract: helper C function to extract the data from a list, see helper.i
    - non_pacman_attributes: list of not directly mapped attributes, which
                             are initialized to None on instance creation
    - cdesc: the middle part of the C function(s), which we want to map
    - local_key_map: dict of attribute names (keys) to callables (func/cls...),
                     applied to any attribute access with the given keys and the
                     original value is replaced with the return value.

    The C function-calls are built like this:

       "alpm_%s_get_%s" % (self.cdesc, attribute_key)

    """
    attributes, ctype, extract, cdesc = None, None, None, None
    local_key_map, non_pacman_attributes = {}, []
    def __init__(self, raw_data):
        """Extracts the data with 'self.extract()' from the container/list
        'raw_data' in case we got a list instead of a specific wanted type
        defined by 'self.ctype'
        """
        self.raw_data = self.extract(raw_data) \
            if raw_data.__class__.__name__ == "alpm_list_t" else raw_data
        self.init_non_pacman_attributes()

    def init_non_pacman_attributes(self):
        """Init all 'self.non_pacman_attributes' from this instance to None"""
        for att in self.non_pacman_attributes:
            setattr(self, att, None)

    def __getattr__(self, key):
        try:
            return self.get_info(key)
        except KeyError, e:
            raise AttributeError(key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all(self.get_info(k) == other.get_info(k)
                       for k in self.attributes)
        raise TypeError("Cannot compare instance of %s with %s" % \
                        (self.__class__.__name__, other.__class__.__name__))

    def __str__(self):
        content = ["%s='%s'" % (k, self.get_info(k)) \
                   for k in self.attributes + self.non_pacman_attributes]
        return "<%s %s>" % (self.__class__.__name__, " ".join(content))
    __repr__  = __str__

    def __getitem__(self, key):
        return self.get_info(key)

    def get_info(self, key):
        """Called from __getattr__ to ask for item-data. This method gets the
        data directly from the backend and maps it to a python object according
        to local_map by key or respectivly GLOBAL_MAP by type. Additionally it
        will return the data from one of the non_pacman_attributes.
        """
        # catch non c-lib/pacman attributes
        if key in self.non_pacman_attributes:
            craw = object.__getattribute__(self, key)
        else:
            # get data from c-lib
            try:
                func = "alpm_%s_get_%s" % (self.cdesc, key)
                craw = getattr(p, func)(self.raw_data)
            except AttributeError as e:
                raise KeyError("An instance of %s contains info for: '%s' "
                               "but not: '%s'" % \
                    (self.__class__.__name__, ", ".join(self.attributes), key))

        # return manipulated value if key in local_key_map
        # if not found, use more general GLOBAL_TYPE_MAP to manipulate value
        # (the keys in GLOBAL_TYPE_MAP are the c-types used in the library)
        try:
            return self.local_key_map[key](craw)
        except KeyError as e:
            return GLOBAL_TYPE_MAP[craw.__class__.__name__](craw)


class PackageItem(AbstractItem):
    """The most widly used *Item in pyalpmm, it holds all information available
    for one specific package. Not all attributes are always accessable,
    for example you can only see the containing files from a local package,
    never from a sync package.
    """
    all_attributes = ["name", "arch", "version", "size", "filename", "desc",
                      "url", "builddate", "installdate", "packager", "md5sum",
                      "isize", "reason", "licenses", "groups", "depends",
                      "optdepends", "conflicts", "provides", "deltas",
                      "replaces", "files", "backup" ]

    attributes = ["name", "arch", "version", "size"]
    non_pacman_attributes = ["repo"]
    ctype = "pmpkg_t"
    extract = p.helper_list_getpkg
    cdesc = "pkg"

    local_key_map = {"reason": FancyReason, "depends": List.DependencyList,
                     "isize": FancySize, "builddate": FancyDateTime,
                     "installdate": FancyDateTime, "size": FancySize,
                     "version": FancyVersion}

class AURPackageItem(AbstractItem):
    """This is still a little messy here. But at this point I doubt I have no
    better/greater/eviler idea, so this is a class describing and wrapping one
    entry from the AUR.
    """
    # this was non-avoidable, aur-naming doesn't follow the pacman naming scheme
    __aur_attributes = {"Version":"version", "Name":"name", "License":"license",
                        "URLPath":"urlpath", "URL":"url", "Description":"desc",
                        "OutOfDate":"outofdate", "NumVotes":"votes", "ID":"id",
                        "CategoryID":"category_id", "LocationID":"location_id"}
    non_pacman_attributes = __aur_attributes.values() + ["repo"]
    attributes = ["name", "version"]
    def __init__(self, dct):
        self.init_non_pacman_attributes()

        for k,v in dct.items():
            setattr(self, self.__aur_attributes[k], v)

class GroupItem(AbstractItem):
    """Keeps all the information about a group, especially their '.pkgs'"""
    attributes = ["name", "pkgs"]
    #non_pacman_attributes = ["repo"]
    ctype = "pmgrp_t"
    extract = p.helper_list_getgrp
    cdesc = "grp"
    local_key_map = { "pkgs" : List.PackageList }

    def __iter__(self):
        for m in self.pkgs:
            yield m

    def __contains__(self, what):
        if what in self.pkgs:
            return True

class DependencyItem(AbstractItem):
    """Stands for a single dependency and its string represantation"""
    attributes = ["name", "mod", "version"]
    ctype = "pmdepend_t"
    extract = p.helper_list_getdep
    cdesc = "dep"

class MissItem(AbstractItem):
    """Represents a missing dependency and the causing package"""
    attributes = ["target", "dep", "causingpkg"]
    ctypes = "pmdepmissing_t"
    extract = p.helper_list_getmiss
    cdesc = "miss"
    local_key_map = {"dep" : DependencyItem }

class FileConflictItem(AbstractItem):
    """Describes a file conflict 'file' between two packages 'target' and 'ctarget'
    with 'type' holding the type of the conflict
    """
    attributes = ["target", "type", "file", "ctarget"]
    ctypes = "pmfileconflicttype_t"
    extract = p.helper_list_getfileconflict
    cdesc = "fileconflict"
    local_key_map = {"type" : FancyFileConflictType }

GLOBAL_TYPE_MAP   = { "pmgrp_t"          : GroupItem,
                      "pmpkg_t"          : PackageItem,
                      "pmdepmissing_t"   : MissItem,
                      "pmdepend_t"       : DependencyItem,
                      "alpm_list_t"      : List.StringList,
                      "pmdepmod_t"       : int,
                      "int"              : int,
                      "str"              : str,
                      "long"             : long,
                      "NoneType"         : lambda a: None }





