# -*- coding: utf-8 -*-
"""

database.py
-----------

This module implements the database middleware between libalpm and pyalpmm.

The DatabaseManager is the API to the alpm library and also manages the
different databases and presents them to the outer world through a consistent
API.

"""

from time import time
from itertools import chain
import re
import os
import urllib

import pyalpmm_raw as p
from item import PackageItem
from lists import PackageList, GroupList, AURPackageList
from tools import CriticalError

class DatabaseError(CriticalError):
    pass

class DatabaseManager(object):
    """Handles the different repositories and databases. Most use-cases will
    nicely fit into the methods this class provides, which are mainly to
    search/examine/compare different packages from different repositories.
    """
    dbs = {}
    local_dbs = {}
    sync_dbs = {}

    def __init__(self, events):
        self.events = events

    def __getitem__(self, tree):
        if isinstance(tree, str):
            try:
                return self.dbs[tree]
            except KeyError, e:
                raise DatabaseError(
                    "The requested db-tree '{0}' is not available".format(tree))
        else:
            raise NotImplementedError(
                "Only string keys are allowed as tree name")

    def __setitem__(self, tree, item):
        if isinstance(tree, slice):
            raise NotImplementedError("Setting a slice - no way")
        elif not issubclass(item.__class__, AbstractDatabase):
            raise TypeError("Cannot set to non-AbstractDatabase derviate")
        self.dbs[tree] = item

    def __delitem__(self, tree):
        if isinstance(tree, slice):
            raise NotImplementedError("Deleting a slice-index - alright?!")
        elif not tree in self.dbs:
            raise KeyError("{0} is not a known db-tree name".format(tree))
        del self.dbs[tree]

    def _get_repositories(self, iterable):
        """Return the appropriate database instance for each string in
        `iterable`

        :param iterable: a set/tuple/list of strings, which all name a database
        """
        if not isinstance(iterable, (tuple, set, list)):
            raise DatabaseError((
                "You have to pass a tuple, set, list or an ancestor of them "
                "as the `repos` keyword argument, "
                "you passed a {0}").format(type(iterable))
            )

        dbs = []
        for dbname in iterable:
            if dbname not in self.dbs:
                raise DatabaseError(
                    "A database called: '{0}' was not found".format(dbname)
                )
            dbs.append(self[dbname])
        return dbs

    def _handle_result(self, result, raise_ambiguous):
        """Handle/PostProcess database result

        :param result: the result(set/list) from the database query
        :param raise_ambiguous: silently give first hit if set to True if not
                                raise :class:`DatabaseError`
        """
        if (len(result) == 1) or (raise_ambiguous is False and len(result) > 1):
            return result.pop()
        elif len(result) == 0:
            return None

        raise DatabaseError(
            ("Found multiple hits with the same query: '{0}'. "
             "Be sure to set the `raise_ambiguous` keyword to `False`, "
             "if you don't want to see this exception occur").format(result)
        )

    def register(self, tree, db):
        """Register a new database to the libalpm backend

        :param tree: the name of the database
        :param db: the :class:`AbstractDatabase` ancestor instance
        """
        if tree in self.dbs:
            raise DatabaseError(
                "You cannot register a database twice: {0}".format(tree)
            )

        if isinstance(db, AbstractDatabase):
            db.tree = tree
            db_shelf = self.local_dbs if tree == "local" else self.sync_dbs
            self[tree] = db_shelf[tree] = db
        else:
            raise DatabaseError("Second parameter in register() must be an \
                                AbstractDatabase ancestor, but is: {0}".\
                                format(db))

    def update_dbs(self, repos=None, force=None, collect_exceptions=True):
        """Update all DBs or those listed in dbs. If 'force' is set,
        then all DBs will be updated. If 'collect_expressions' is set to
        False, then a un-successful database update will raise a
        :class:`DatabaseError`

        :param repos: the repos to update
        :param force: force updating the repositories
        :param collect_exceptions: if True the occuring exceptions will not be
                                   raised, they will be showed at the end of the
                                   transaction
        """
        repos = self._get_repositories(repos or self.sync_dbs.keys())
        force = force and 1 or 0
        out, exceptions = [], []
        for repo in repos:
            try:
                ret = repo.update(force)
            except DatabaseError as e:
                if not collect_exceptions:
                    raise e
                # if collect_exceptions is True, just save exception
                exceptions.append(e)
                self.events.DatabaseUpdateError(repo=repo.tree)
            else:
                if ret:
                    self.events.DatabaseUpdated(repo=repo.tree)
                else:
                    self.events.DatabaseUpToDate(repo=repo.tree)

        if len(exceptions) > 0:
            print "[-] the following exceptions occured, while updating"
            for ex in exceptions:
                print "[e] {0}".format(ex)


    def search_package(self, repos=None, **kw):
        """Search for a package (in the given repos) with given properties
        i.e. pass name="xterm"

        :param repos: the list of repository-names to search in
        :param kw: the searchquery
        """
        repos = self._get_repositories(repos or self.dbs.keys())
        for repo in repos:
            pkglist = repo.search_package(**kw)
            if pkglist is None:
                continue
            for pkg in pkglist:
                pkg.repo = repo.tree
                yield pkg

    def search_local_package(self, **kw):
        """A shortcut to search all local packages for the given query

        :param kw: the search query
        """
        return self.search_package(repos=self.local_dbs.keys(), **kw)

    def search_sync_package(self, **kw):
        """A shortcut to search the sync repositories for the given query

        :param kw: the search query
        """
        return self.search_package(repos=self.sync_dbs.keys(), **kw)

    def get_packages(self, repos=None):
        """Get all packages from all databases, actually returns an iterator

        :param repos: a list of the repositories, which will be used for this
                      operation
        """
        repos = self._get_repositories(repos or self.dbs.keys())
        for repo in repos:
            pkglist = repo.get_packages()
            for pkg in pkglist:
                pkg.repo = repo.tree
                yield pkg

    def get_local_packages(self):
        """Returns an iterator over all local packages - shortcut"""
        return self.get_packages(self.local_dbs.keys())

    def get_sync_packages(self):
        """Returns an iterator over all sync repository packages - shortcut"""
        return self.get_packages(self.sync_dbs.keys())

    def get_groups(self, repos=None):
        """Get all groups from all databases

        :param repos: a list of the repositiory names, which should be used
        """
        repos = self._get_repositories(repos or self.dbs.keys())
        return chain(*[repo.get_groups() for repo in repos])

    def get_local_groups(self):
        """Get only locally available groups - shortcut"""
        return self.get_groups(repos=self.local_dbs.keys())

    def get_sync_groups(self):
        """Get all sync-able groups"""
        return self.get_groups(repos=self.sync_dbs.keys())

    # to be complete, here should be: get_local_group(name)
    #                                 get_sync_group(name)


    def get_package(self, pkgname, repos=None, raise_ambiguous=False):
        """Return package either for sync or for local repo

        You can either give the package name in the full repo notation,
        i.e.: extra/xterm (no leading slash and no version!) or you can
        pass just a pkgname like "xterm" and also pass a list of strings to
        the repos keyword and only the included repositories will be
        checked during the search!

        If `repos` contains a not known repository, throw a
        :class:`DatabaseError`

        :param pkgname: the package name to look for
        :param repos: a list of the repositiory names, which will be used to
                      search the package name inside (optional)
        :param raise_ambiguous: if True, will raise :class:`DatabaseError` if
                                there is more than one hit, if False, just
                                return the first hit (optional)
        """

        # check for leading "/"
        if pkgname.startswith("/"):
            raise DatabaseError(
                "The passed 'pkgname' started with a '/', \
                this is not a valid package name"
            )

        # check for repository package notation
        if "/" in pkgname:
            try:
                repo, pkgname = pkgname.split("/")
                repos = [repo]
            except:
                raise DatabaseError(
                    "The given `pkgname` was not correctly formated: '{0}'". \
                    format(pkgname)
                )
        repos = self._get_repositories(repos or self.dbs.keys())

        query = {"name__eq": pkgname}
        found = []
        for repo in repos:
            for pkg in repo.search_package(**query):
                pkg.repo = repo.tree
                #found = sum((repo.search_package(**query) for repo in repos), [])
                found.append(pkg)

        try:
            return self._handle_result(found, raise_ambiguous)
        except DatabaseError as e:
            e.format("name__eq={0}".format(pkgname))
            raise e

    def get_local_package(self, pkgname, raise_ambiguous=False):
        """Get info about one package `pkgname`, from the local repository

        :param pkgname: the package name to look for
        :param raise_ambiguous: if True, will raise :class:`DatabaseError` if
                                there is more than one hit, if False, just
                                return the first hit (optional)
        """
        return self.get_package(
            pkgname,
            repos=self.local_dbs.keys(),
            raise_ambiguous=raise_ambiguous
        )

    def get_sync_package(self, pkgname, raise_ambiguous=False):
        """Get info about one remote-package called `pkgname`

        :param pkgname: the package name to look for
        :param raise_ambiguous: if True, will raise :class:`DatabaseError` if
                                there is more than one hit, if False, just
                                return the first hit (optional)
        """
        return self.get_package(
            pkgname,
            repos=self.sync_dbs.keys(),
            raise_ambiguous=raise_ambiguous
        )

    def get_group(self, grpname, repos=None, raise_ambiguous=False):
        """Get one group from the database

        :param grpname: the name of the searched group
        :param repos: (optional) arg is to search only in the given databases
        :param raise_ambiguous: if True, will raise :class:`DatabaseError` if
                                there is more than one hit, if False, just
                                return the first hit (optional)
                                As there are groups, which are split over
                                several repos, this option makes no sense...!!!
        """
        db_objs = self._get_repositories(repos or self.sync_dbs.keys())

        grps = []
        for grp_list in (db.get_groups() for db in db_objs):
            for grp in grp_list:
                if grp.name == grpname:
                    grps.append(grp)
        return grps

    # untested
    def set_package_reason(self, pkg, reason_id):
        p.alpm_db_set_pkgreason(self.dbs["local"], pkg.name, reason_id)

class AbstractDatabase(object):
    """Implements an abstract interface to one database"""
    def __del__(self):
        p.alpm_db_unregister(self.db)

    def __contains__(self, pkgname):
        res = self.search_package(name=pkgname)
        for pkg in res:
            if pkg.name == pkgname:
                return True
        return False

    def search_package(self, **kw):
        """Search this database for a given query"""
        return self.get_packages().search(**kw)

    def get_packages(self):
        """Get all available packages in this database"""
        return PackageList(p.alpm_db_get_pkgcache(self.db))

    def get_groups(self):
        """Get all available groups in this database"""
        return GroupList(p.alpm_db_get_grpcache(self.db))

class LocalDatabase(AbstractDatabase):
    """Represents the local database"""
    def __init__(self):
        self.db = p.alpm_db_register_local()
        self.tree = "local"

class SyncDatabase(AbstractDatabase):
    """Represents any sync-able or remote database"""
    def __init__(self, tree, url):
        self.db = p.alpm_db_register_sync(tree)
        self.tree = tree
        if p.alpm_db_setserver(self.db, url) == -1:
            raise DatabaseError(
                "Could not connect database: {0} to url/server: {1}".format(
                    tree, url
                ))

    def update(self, force=None):
        """Call the underlying c-function to update the database

        :param force: the database ignores a possible no-need-to-update
        """
        r = p.alpm_db_update(force, self.db)
        if r < 0:
            raise DatabaseError(
                "Database '{0}' could not be updated".format(self.tree))
        elif r == 1:
            return False
        return True

class AURDatabase(SyncDatabase):
    """Represents the AUR"""
    def __init__(self, config):
        self.config = config
        self.tree = "aur"

    def get_packages(self):
        """Just give the AURPackageList, which wrapps all queries"""
        return AURPackageList(self.config)

    def get_groups(self):
        """There are no groups in AUR, so just returns an empty list"""
        return []

    def update(self, force=None):
        """There is no need to update because we always send an RPC request"""
        return True
