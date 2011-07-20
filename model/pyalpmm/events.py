# -*- coding: utf-8 -*-
"""

events.py
-----------

This module keeps all the possible events that can occur.
Your application you will most likly derive from Events and add, overwrite
some methods to fit them for your needs.

Every event can simply get a callback function connected by just implementing
a method which has the exact name of the event.
"""

import sys
import datetime

from tools import AskUser

class Events(object):
    last_event, logfile = None, None
    names = (# general events
             "StartCheckingDependencies",         # ()
             "StartCheckingFileConflicts",        # ()
             "StartResolvingDependencies",        # ()
             "StartCheckingInterConflicts",       # ()
             "StartInstallingPackage",            # (pkg: PackageItem)
             "StartRemovingPackage",              # (pkg: PackageItem)
             "StartUpgradingPackage",             # (pkg: PackageItem)
             "StartCheckingPackageIntegrity",     # ()
             "StartRetrievingPackages",           # (repo: str)
             "DoneInstallingPackage",             # (pkg: PackageItem)
             "DoneRemovingPackage",               # (pkg: PackageItem)
             "DoneUpgradingPackage",              # (pkg, from_pkg: PackageItem)
             # alpm "questions"
             "AskInstallIgnorePkgRequired",       # (pkg, req_pkg: PackageItem)
             "AskInstallIgnorePkg",               # (pkg: PackageItem)
             "AskUpgradeLocalNewer",              # (pkg: PackageItem)
             "AskRemoveHoldPkg",                  # (pkg: PackageItem)
             "AskReplacePkg",                     # (pkg, rep_pkg: PackageItem, repo: str)
             "AskRemoveConflictingPackage",       # (pkg, conf_pkg: str)
             "AskRemoveCorruptedPackage",         # (pkg: PackageItem)
             # database updates
             "DatabaseUpToDate",                  # (repo: str)
             "DatabaseUpdated",                   # (repo: str)
             "DatabaseUpdateError",               # (repo: str)
             # transaction info
             "DoneTransactionInit",               # ()
             "DoneTransactionDestroy",            # ()
             "DoneSettingTargets",                # (targets: (pkglist: list of str, grplist: list of str)
             "DoneTransactionPrepare",            # ()
             "DoneTransactionCommit",             # ()
             "StartPreAURTransaction",            # (targets: (list of str) aur_targets: (list of str)
             # System info
             "ProcessingPackages",                # (add, remove: lists of PackageItem or None)
             "ProcessingAURPackages",             # (add: list of AURPackageItem or None)
             "ReInstallingPackage",               # (pkg: PackageItem)
             # session info
             "StartInitSession",                  # ()
             "DoneInitSession",                   # ()
             "DoneApplyConfig",                   # ()
             # options
             "DoneReadingConfigFile",             # ()
             # progress handling
             "StartNewDownload",                  # (filename: str)
             "ProgressDownload",                  # (transfered, filecount: int, filename: str)
             "ProgressDownloadTotal",             # (total: int, pkgs: list of PackageItem)
             "ProgressInstall",                   # (pkgname: str, percent: int)
             "ProgressRemove",                    # (pkgname: str, percent: int)
             "ProgressUpgrade",                   # (pkgname: str, percent: int)
             "ProgressConflict",                  # (pkgname: str, percent: int)
             # building
             "DoneBuildDirectoryCleanup",
             "StartABSBuildPrepare",
             "StartAURBuildPrepare",
             "DoneBuildPrepare",
             "StartBuild",
             "DoneBuild",
             "StartBuildEdit",
             "DoneBuildEdit",

             # log - not a real event though
             "Log",

             # problems/errors
             # (high level events, only available within a System instance)
             # (if you're using lowlvl interface,
             #  those will be thrown as exceptions)
             "PackageNotFound",                   # (e: instance of NotFoundError)
             "UnsatisfiedDependencies",           # (e: instance of UnsatisfiedDependenciesError)
             "FileConflictDetected",              # (e: instance of FileConflictError)
             "ConflictingDependencies",           # (e: instance of ConflictingDependenciesError)
             "NothingToBeDone",                   # (e: instance of NothingToBeDoneError)
             "NotRoot",                           # (e: instance of NotRootError)
             "UserAbort",                         # (e: instance of UserError)
             "BuildProblem",                      # (e: instance of BuildError)
        )
    def __init__(self):
        self.bound_events = [meth for meth in dir(self) if meth in self.names]

    def __setattr__(self, attr, value):
        if attr in self.names:
            self.bound_events.append(attr)
        return object.__setattr__(self, attr, value)

    def __getattribute__(self, attr):
        if attr in object.__getattribute__(self, "names"):
            object.__getattribute__(self, "Log")(event=attr, data={})
            if attr not in object.__getattribute__(self, "bound_events"):
                return object.__getattribute__(self, "doNothing")
        return object.__getattribute__(self, attr)

    def doNothing(self, **kw):
        """A dummy callback function, just forwards the event to the logger"""
        pass

    def Log(self, **kw):
        """The logger, this will be replaced with logger from python
        in the near future

        - kw["event"]: name of the last occured event
        - kw["data"]: to-be-logged data as a dict
        """
        if self.logfile:
            # sometimes i am just producing this:
            file(self.logfile, "a").write("%20s - [%25s] %s\n" % \
                (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                 kw["event"],
                 " ".join("{0}: {1}".format(k,v) for k,v in kw["data"].items())))

    def AskInstallIgnorePkgRequired(self, **kw):
        """Should pyalpmm upgrade a package, which is a member of the
        IgnorePkg or IgnoreGrp lists and is required by another package?

        - kw["pkg"]: instance of :class:`PackageItem` - demanding package
        - kw["req_pkg"]: instance of :class:`PackageItem` - required package
        """
        if AskUser(("[?] %s wants to have %s, "
                    "but it is in IgnorePkg/IgnoreGrp - proceed?") % \
                   (kw["pkg"].name, kw["req_pkg"].name)).answer == "y":
            return 1
        return 0

    def AskInstallIgnorePkg(self, **kw):
        """A package, which you choose to upgrade, is a member of the IgnoreGrp
        or the IgnorePkg group.

        - kw["pkg"]: instance of :class:`PackageItem`
        """
        if AskUser("[?] %s is in IgnorePkg/IgnoreGrp - proceed anyway?" % \
                   kw["pkg"].name).answer == "y":
            return 1
        return 0

    def AskUpgradeLocalNewer(self, **kw):
        """The local version of the package is newer than the one ,which is
        about to be upgraded.

        - kw["pkg"]: instance of :class:`PackageItem`
        """
        if AskUser("[?] %s's local version is newer - upgrade anyway?" % \
                   kw["pkg"].name).answer == "y":
            return 1
        return 0

    def AskRemovePkg(self, **kw):
        """A member of the HoldPkg list is about to be removed.

        - kw["pkg"]: instance of :class:`PackageItem`
        """
        if AskUser("[?] %s is in HoldPkg - remove anyway?" % \
                   kw["pkg"]).answer == "y":
            return 1
        return 0

    def AskReplacePkg(self, **kw):
        """Should one package be replaced by another package?

        - kw["pkg"]: instance of :class:`PackageItem` - "old" package
        - kw["repo"]: name of the repository
        - kw["rep_pkg"]: instance of :class:`PackageItem` - "new" package
        """
        if AskUser("[?] %s should be replaced with %s/%s - proceed?" % \
            (kw["pkg"].name, kw["repo"], kw["rep_pkg"].name)).answer == "y":
            return 1
        return 0

    def AskRemoveConflictingPackage(self, **kw):
        """Should pyalpmm remove one of two conflicting packages now?

        - kw["pkg"]: instance of :class:`PackageItem` - stays
        - kw["conf_pkg"]: instance of :class:`PackageItem` - to-be-removed
        """
        if AskUser("[?] Package {0} conflicts with {1} - remove {1}? (y/n) ".\
                   format(kw["pkg"], kw["conf_pkg"])).answer == "y":
            return 1
        return 0

    def AskRemoveCorruptedPackage(self, **kw):
        """We found a corrupted package and want to remove it.

        - kw["pkg"]: instance of :class:`PackageItem`
        """
        if AskUser("[?] %s is corrupted - remove it?" % \
                   kw["pkg"].name).answer == "y":
            return 1
        return 0

