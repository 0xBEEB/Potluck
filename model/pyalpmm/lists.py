# -*- coding: utf-8 -*-
"""

lists.py
-----------

This module implements fitting containers for *Item instances. Actually
it is a wrapper for the alpm_list_t implementation, which transparently
provides a pythonic API without caring about the C library.

Mostly your application will use these lists, as they create the *Item instances
on-the-fly and also forward the Python operations on the list to the appropriate
C function call.
"""
import os, sys
import heapq
from itertools import chain
import urllib
import re
import operator as ops

import pyalpmm_raw as p

import item as Item
from options import PyALPMMConfiguration as config

class LazyList(object):
    """Wraps the alpm_list_t C types into a Python object, which can be
    accessed like a regular list.
    """

    search_endings = {
        "__eq": ops.eq,
        "__in": lambda q, s: s.find(q) != -1,
        "__ne": ops.ne
    }

    def __init__(self, raw_list):
        self.raw_list = raw_list

    def __len__(self):
        return p.alpm_list_count(self.raw_list)

    def __getitem__(self, i):
        if isinstance(i, str):
            return self.search(name=i)
        elif isinstance(i, slice):
            return chain(self.create_item(self.get_one_item(x)) \
                for x in xrange(i.start or 0, i.stop, i.step or 1))
        return self.create_item(self.get_one_item(i))

    def __iter__(self):
        cur = p.alpm_list_first(self.raw_list)
        while cur:
            yield self.create_item(cur)
            cur = p.alpm_list_next(cur)

    def _parse_keywords(self, kw):
        """This method parses the keyword keys for the known special endings.
        Return a new dict only with a tuple containing the cleaned up value
        and then the operator to use for comparision.

        The keys passed in kwargs can have some special endings:
        "__in"    =>    (default) true if the query is part of the target str
                        You never have to use this, as this is the (default)
        "__eq"    =>    check query for equality against the string
        "__ne"    =>    check for in-equality
        """
        query = {}
        for k, v in kw.items():
            for ending, operator in self.search_endings.items():
                if k.endswith(ending):
                    k = k[:-len(ending)]
                    query[k] = (v, operator)
                    break
            else:
                query[k] = (v, self.search_endings["__in"])
        return query

    def get_one_item(self, i):
        """Return the item at the index 'i'"""
        if isinstance(i, int):
            return p.alpm_list_nth(self.raw_list, i)
        raise KeyError("Can only get item with an integer index")

    def create_item(self, item):
        """Create one *Item of the correct type for this list and ctype"""
        return Item.AbstractItem()

    def order_by(self, key):
        # is this true what this jackass wrote there
        raise NotImplementedError("General order_by for LazyList not availible")

    def search(self, s):
        """A not so well over-thought search - TODO!"""
        li = []
        for hay in self:
            if s in hay:
                yield hay

    def __str__(self):
        return "<%s #=%s content=(%s)>" % (
            self.__class__.__name__, len(self),
            ", ".join(str(s) for s in self)
        )

class MissList(LazyList):
    """Holds MissItem objects"""
    def create_item(self, raw_data):
        """Return a new MissItem created with 'raw_data'"""
        return Item.MissItem(raw_data)

class DependencyList(LazyList):
    """Holds DependencyItem objects"""
    def create_item(self, raw_data):
        """Give a DependencyItem back for the given 'raw_data'"""
        return Item.DependencyItem(raw_data)

    def __str__(self):
        return "<%s #=%s content=(%s)>" % (
            self.__class__.__name__,
            len(self),
            ", ".join(s.name for s in self)
        )

class PackageList(LazyList):
    """Holds PackageItem objects"""

    def create_item(self, raw_data):
        """Creates a PackageItem from the passed raw_data"""
        return Item.PackageItem(raw_data)

    def search(self, **kw):
        """This search checks if the given query `kw` matches one of the
        :class:`PackageItem` instances kept by the list. Each object is checked,
        wheater its attributes match the keys and the attribute-values the
        values from the kwargs dict.

        :param kw: keyword arguments with the actual query,
                   magic endings are supported
        """
        res = set()
        kw = self._parse_keywords(kw)
        for pkg in self:
            if any(op(v, pkg.get_info(k) or "") \
                   for k, (v, op) in kw.items()):
                res.add(pkg)
        return list(res)

    # this method looks a bit obsolete/unused... hmmm
    def order_by(self, k):
        """Yield the list contents in an order defined by the passed key `k`

        :param k: the key-column, which should be used to order the output
        """
        lst = [(v.get_info(k),v) for v in self]
        heapq.heapify(lst)
        pop = heapq.heappop
        out = []
        while lst:
            yield pop(lst)[1]

class AURPackageList(PackageList):
    """Holds evil AURPackageItem objects.
    This class implements a full blown wrapper to work with AURPackages as
    easy as with any other "official" package repository. Data is aquired
    through RPC.

    :param config: a :class:`pyalpmm.options.PyALPMMConfiguration` instance
    """
    _package_database_cache = None
    _package_list_pattern = re.compile(r'a href\=\"([^\"]+)\"')
    def __init__(self, config):
        self.config = config

    def __len__(self):
        return len(self.package_database)

    def __getitem__(self, i):
        return self.create_item({"Name": self.package_database[i],
                                 "Version": "(aur)"})
    def search(self, **kw):
        """Search for a package with an RPC call to the AUR repository
        We won't handle any kind of suffix in the kw keys like in PackageList
        I see no real sense in this, as long as AUR and the regular repos not
        even have the same naming scheme

        :param kw: the search query as a dict
        """
        # the AUR can only be searched for names
        kw = self._parse_keywords(kw)
        if "name" not in kw:
            return []

        data = {"type": "search", "arg": kw["name"][0]}
        rpc_url = self.config.aur_url + self.config.rpc_command
        res = eval(urllib.urlopen(rpc_url % data).read())["results"]
        out = []

        # if result is just a string, we got an error
        if isinstance(res, str):
            return []

        candidates = [self.create_item(data_dct) for data_dct in res]

        out = []
        for pkg in candidates:
            pkg.repo = "aur"
            if any(op(v, pkg.get_info(k)) for k, (v, op) in kw.items()):
                out.append(pkg)

        return out

    def create_item(self, dct):
        """Create a AURPackageItem from a given input `dct`

        :param dct: the dictionary which holds all the retrieved package data
        """
        return Item.AURPackageItem(dct)

class GroupList(LazyList):
    """A list for GroupItems"""
    def create_item(self, raw_data):
        """Create the GroupItem from the input `raw_data`

        :param raw_data: the raw C-data of this group
        """
        return Item.GroupItem(raw_data)

    def search(self, **kw):
        """Return an iterator over the groups matching the keyword conditions.

        :param kw: keyword arguments with the actual query,
                   magic endings are supported
        """
        kw = self._parse_keywords(kw)
        return (grp for grp in self \
                if any(op(v, grp.get_info(k)) for k, (v, op) in kw.items()))

    def order_by(self, k):
        """Return the :class:`GroupItem` instances ordered

        :param k: the key the ordering is dependent on"""
        li = list(x for x in self)
        li.sort(lambda a,b: (a.get_info(k),b))
        return li

class FileConflictList(LazyList):
    """A list of FileConflictItem instances"""
    def create_item(self, raw_data):
        """Creating a FileConflictItem from `raw_data`"""
        return Item.FileConflictItem(raw_data)

class StringList(LazyList):
    """A list just holding simple strings"""
    def create_item(self, raw_data):
        """Get the data with a C helper function"""
        return str(p.helper_list_getstr(raw_data))

    def order(self):
        """Return the strings ordered"""
        li = list(x for x in self)
        li.sort()
        return li

    def __contains__(self, what):
        """Test wheather 'what' is in one of our strings"""
        for s in self:
            if what in s:
                return True
        return False