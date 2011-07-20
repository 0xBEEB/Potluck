# -*- coding: utf-8 -*-
"""

transaction.py
--------------

This module implements the whole transaction handling between pyalpmm, libalpm
and the filesystem.

In general you work with an *Transaction like this:

with SyncTransaction(session, ["xterm"]) as transobj:
    transobj.aquire()
    # here your transaction is pending, you can get the processed packages:
    for pkg in transobj.get_targets():
        print pkg.name
        print pkg.version
    transobj.commit()

Obviously you can only start a transaction if you are root.
"""

#  int alpm_trans_interrupt(void); INTERRUPT FOR TRANSACTION FOR SIGNALS


import os, sys

import pyalpmm_raw as p

from pyalpmm.database import *
from pyalpmm.tools import AskUser, CriticalError, UserError
from pyalpmm.lists import MissList, StringList, DependencyList, FileConflictList
from pyalpmm.item import PackageItem
from pyalpmm.pbuilder import PackageBuilder, BuildError

class NotFoundError(CriticalError):
    """Target cannot be added to the transaction"""
    def __init__(self, msg, targets):
        self.targets = targets
        super(NotFoundError, self).__init__(msg.format(", ".join(targets)))

class UnsatisfiedDependenciesError(CriticalError):
    """Target cannot be removed, because there are packages depending on it"""
    def __init__(self, msg, pkgs):
        self.data = pkgs
        super(UnsatisfiedDependenciesError, self).__init__(msg)

class FileConflictError(CriticalError):
    """One or more target-package-files conflict with local files"""
    def __init__(self, msg, data):
        self.data = [{
            "type": item.type, "file": item.file, "target_pkg": item.ctarget,
            "local_pkg": item.target if p.PM_FILECONFLICT_FILESYSTEM else None
        } for item in data]
        super(FileConflictError, self).__init__(msg)

class NothingToBeDoneError(CriticalError):
    """Could not find something to do, aborting"""

class ConflictingDependenciesError(CriticalError):
    """Could not resolve (most likely the user said to not replace the
    conflicting package) dependency conflict"""

class TransactionError(CriticalError):
    """TransactionError(s) gets a special treatment for different types of
    TransactionErrors that can occur. The concept is not soo bad, but far away
    from complete I guess.
    """

class Transaction(object):
    """The baseclass for all *Transaction classes.
    Forwards alot of events to the pyalpmm event handler and manages - means
    initializes, prepares, adds targets to and commits *Transaction instances.

    :param session: instance of :class:`pyalpmm.session.Session`
    :param targets: a list of strings identifying the packages to process
    """
    def __init__(self, session, targets=None):
        self.session = session
        self.events = self.session.config.events
        self.targets = targets
        self.__backend_data = None

    def aquire(self):
        """Aquire a transaction from libalpm by setting all necassary callback
        functions and values, then call alpm_trans_init() and pray
        """
        if self.session.config.rights != "root":
            raise TransactionError(
                "You must be root to initialize a transaction")

        # set callbacks for download and totaldownload
        p.alpm_option_set_dlcb(self.__callback_download_progress)
        p.alpm_option_set_totaldlcb(self.__callback_download_total_progress)

        # this one to set alernative downloader
        #p.alpm_cb_fetch(const char *url, const char *localpath, int force)

        # init transaction, including the rest of the callbacks
        if p.alpm_trans_init(
            self.session.config.transaction_flags,
            self.__callback_event,
            self.__callback_conv,
            self.__callback_progress
        ) == -1:
            if p.get_errno() == p.PM_ERR_HANDLE_LOCK:
                raise TransactionError("The local database is locked")
            raise TransactionError("Could not initialize the transaction")

        # list of packages and groups
        self.pkg_search_list = self.session.db_man.get_packages()
        self.grp_search_list = self.session.db_man.get_groups()

        self.events.DoneTransactionInit()

        # if targets were directly passed at __init__ set them and .prepare()
        if self.targets:
            self.set_targets(self.targets)
            self.prepare()

    def prepare(self):
        """After setting the targets, the transaction is ready to be prepared.
        Use helper functions in C (pyalpmm_raw/helper.i) to construct a
        alpm_list_t in C space on which the transaction can work on.
        """
        self.__backend_data = p.get_list_buffer_ptr()
        if p.alpm_trans_prepare(self.__backend_data) == -1:
            self.handle_error(p.get_errno())

        self.targets = self.get_targets()
        if len(self.targets["remove"]) + len(self.targets["add"]) == 0:
            raise NothingToBeDoneError("Nothing to be done...")

        self.events.DoneTransactionPrepare()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    # those 5 methods wrap the Transaction events to the Events instance
    def __callback_download_progress(self, fn, transfered, filecount):
        if transfered == 0:
            self.events.StartNewDownload(filename=fn)
        self.events.ProgressDownload(
            filename=fn, transfered=transfered, filecount=filecount
        )
    def __callback_download_total_progress(self, total):
        self.events.ProgressDownloadTotal(total=total, pkgs=self.get_targets()["add"])
    def __callback_event(self, event, data1, data2):
        if event == p.PM_TRANS_EVT_CHECKDEPS_START:
            self.events.StartCheckingDependencies()
        elif event == p.PM_TRANS_EVT_FILECONFLICTS_START:
            self.events.StartCheckingFileConflicts()
        elif event == p.PM_TRANS_EVT_RESOLVEDEPS_START:
            self.events.StartResolvingDependencies()
        elif event == p.PM_TRANS_EVT_INTERCONFLICTS_START:
            self.events.StartCheckingInterConflicts()
        elif event == p.PM_TRANS_EVT_ADD_START:
            self.events.StartInstallingPackage(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_EVT_ADD_DONE:
            self.events.DoneInstallingPackage(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_EVT_REMOVE_START:
            self.events.StartRemovingPackage(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_EVT_REMOVE_DONE:
            self.events.DoneRemovingPackage(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_EVT_UPGRADE_START:
            self.events.StartUpgradingPackage(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_EVT_UPGRADE_DONE:
            self.events.DoneUpgradingPackage(
                pkg=PackageItem(data1), from_pkg=PackageItem(data2))
        elif event == p.PM_TRANS_EVT_INTEGRITY_START:
            self.events.StartCheckingPackageIntegrity()
        elif event == p.PM_TRANS_EVT_RETRIEVE_START:
            self.events.StartRetrievingPackages(repo=data1)
        else:
            pass
    def __callback_conv(self, event, data1, data2, data3):
        if event == p.PM_TRANS_CONV_INSTALL_IGNOREPKG:
            if data2:
                return self.events.AskInstallIgnorePkgRequired(
                    pkg=PackageItem(data1), req_pkg=PackageItem(data2))
            return self.events.AskInstallIgnorePkg(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_CONV_LOCAL_NEWER:
            if self.session.config.download_only:
                return 1
            return self.events.AskUpgradeLocalNewer(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_CONV_REMOVE_PKGS:
            return self.events.AskRemovePkg(pkg=PackageItem(data1))
        elif event == p.PM_TRANS_CONV_REPLACE_PKG:
            return self.events.AskReplacePkg(
                pkg=PackageItem(data1), rep_pkg=PackageItem(data2), repo=data3)
        elif event == p.PM_TRANS_CONV_CONFLICT_PKG:
            return self.events.AskRemoveConflictingPackage(
                pkg=data1, conf_pkg=data2)
        elif event == p.PM_TRANS_CONV_CORRUPTED_PKG:
            return self.events.AskRemoveCorruptedPackage(pkg=data1)
        else:
            return 0

    def __callback_progress(self, event, pkgname, perc, count, remain):
        if event == p.PM_TRANS_PROGRESS_ADD_START:
            self.events.ProgressInstall(
                pkgname=pkgname, percent=perc, howmany=count, remain=remain)
        elif event == p.PM_TRANS_PROGRESS_UPGRADE_START:
            self.events.ProgressUpgrade(
                pkgname=pkgname, percent=perc, howmany=count, remain=remain)
        elif event == p.PM_TRANS_PROGRESS_REMOVE_START:
            self.events.ProgressRemove(
                pkgname=pkgname, percent=perc, howmany=count, remain=remain)
        elif event == p.PM_TRANS_PROGRESS_CONFLICTS_START:
            self.events.ProgressConflict(
                pkgname=pkgname, percent=perc, howmany=count, remain=remain)

    def release(self):
        """Release the transaction, this is the official end for the instance"""
        p.alpm_trans_release()
        self.events.DoneTransactionDestroy()

    def get_targets(self):
        return {
            "remove": PackageList(p.alpm_trans_get_remove()),
            "add": PackageList(p.alpm_trans_get_add())
        }

    def set_targets(self, tars):
        """Add several targets taken from the list 'tars' to the transaction"""
        out, grps_toinstall, toinstall = [], set(), []
        db_man = self.session.db_man

        if self.trans_type == "sync":
            grps = db_man.get_sync_groups()
        elif self.trans_type == "local":
            grps = db_man.get_local_groups()
        else:
            grps = []

        for t in tars:
            if t in (g.name for g in grps):
                grps = db_man.get_group(t, self.session.config.repos)
                for grp in grps:
                    for pkg in grp.pkgs:
                        self.add_target(pkg.name)
                        toinstall += [pkg.name]
                    grps_toinstall.add(grp.name)
            else:
                try:
                    self.add_target(t)
                    toinstall += [t]
                except TransactionError as e:
                    out += [t]

        # need some check WHY targets could not be added! (fileconflicts...)
        if len(out) > 0:
            raise NotFoundError(
                "Not all targets could be added, the remaining are: {0}", out)


        #self.targets = (toinstall, grps_toinstall)
        self.events.DoneSettingTargets(targets=self.targets)

    def commit(self):
        """Commit this transaction and let libalpm apply the changes to the
        filesystem and the databases
        """
        if len(self.targets["add"]) + len(self.targets["remove"]) == 0:
            raise NothingToBeDoneError("Nothing to be done...")

        if p.alpm_trans_commit(self.__backend_data) == -1:
            self.handle_error(p.get_errno())

        self.events.DoneTransactionCommit()

    def handle_error(self, errno):
        """Handle specific error types, if errno is unknown - show errno and
        alpm_strerror
        """
        err_msg = "ALPM error: {0} ({1})"
        if errno == p.PM_ERR_UNSATISFIED_DEPS:
            raise UnsatisfiedDependenciesError(
                "There are unsatisfied dependencies for this operation:",
                MissList(p.get_list_from_ptr(self.__backend_data))
            )
        elif errno == p.PM_ERR_FILE_CONFLICTS:
            raise FileConflictError(
                "At least one target package creates a file conflict:",
                FileConflictList(p.get_list_from_ptr(self.__backend_data))
            )
        elif errno == p.PM_ERR_CONFLICTING_DEPS:
            raise ConflictingDependenciesError(
                "The conflicting dependencies could not be resolved")
        else:
            raise TransactionError(
                err_msg.format(p.alpm_strerror(errno), errno))

class SyncTransaction(Transaction):
    """Sync the 'targets' with the system"""
    trans_type = "sync"

    def add_target(self, target):
        if "/" in target:
            pos = target.find("/")
            ret = p.alpm_sync_dbtarget(target[:pos], target[pos+1:])
        else:
            ret = p.alpm_sync_target(target)

        if ret == -1:
            self.handle_error(p.get_errno())

class RemoveTransaction(Transaction):
    """Remove the given 'targets' from the system"""
    trans_type = "remove"

    def __init__(self, session, targets=None):
        super(RemoveTransaction, self).__init__(session, targets=targets)

        self.pkg_search_list = self.session.db_man["local"].get_packages()
        self.grp_search_list = self.session.db_man["local"].get_groups()

    def add_target(self, target):
        ret = p.alpm_remove_target(target)

        if ret == -1:
            self.handle_error(p.get_errno())

class UpgradeTransaction(Transaction):
    """Upgrade the given targets on the system"""
    trans_type = "upgrade"

    def add_target(self, target):
        ret = p.alpm_add_target(target)

        if ret == -1:
            self.handle_error(p.get_errno())

class AURTransaction(UpgradeTransaction):
    """The AURTransaction handles all the building, installing of an AUR package
    """
    trans_type = "aur"

    def add_target(self, pkgname):
        pkg = self.session.db_man.get_sync_package(pkgname)
        if pkg is None:
            raise DatabaseError(
                "I haven't found a file with the pkgname: {0} inside the AUR".\
                format(pkgname)
            )
        p = PackageBuilder(self.session, pkg)
        if self.session.config.build_edit:
            p.edit()
        if self.session.config.build_cleanup:
            p.cleanup()
        if self.session.config.build_prepare:
            p.prepare()
        p.build()

        if self.session.config.build_install:
            super(AURTransaction, self).add_target(p.pkgfile_path)

class SysUpgradeTransaction(SyncTransaction):
    """The SysUpgradeTransaction upgrades the whole system with the latest
    available packages.
    """
    trans_type = "sysupgrade"

    def aquire(self):
        """As we have no targets here, we can prepare() after aquire()"""
        super(SysUpgradeTransaction, self).aquire()
        self.prepare()

    def prepare(self):
        """For preparation there is a special C function, which we use to
        get the needed targets into the transaction
        """
        if p.alpm_sync_sysupgrade(self.session.config.allow_downgrade) == -1:
            self.handle_error(p.get_errno())
        super(SysUpgradeTransaction, self).prepare()

class DatabaseUpdateTransaction(SyncTransaction):
    """Update all (or just the passed) databases"""
    trans_type = "update"

    def __init__(self, session, dbs=None):
        super(DatabaseUpdateTransaction, self).__init__(session)
        self.target_dbs = dbs

    def prepare(self):
        """No need to prepare for a :class:`DatabaseUpdateTransaction`"""
        pass

    def commit(self):
        """The actual work is given to the *Database instances, they have to
        implement the updating by themselves.
        """
        dbs, sess = self.target_dbs, self.session
        if not dbs:
            o = sess.db_man.update_dbs(force=self.session.config.force)
        elif isinstance(dbs, list) and all(isinstance(x, str) for x in dbs):
            o = sess.db_man.update_dbs(repos=dbs, force=sess.config.force)
        elif isinstance(dbs, str):
            o = sess.db_man.update_dbs(repos=[dbs], force=sess.config.force)
        else:
            raise TypeError(("The passed databases must be either a list of "
                             "strings or only one string, not: {0}").
                            format(dbs))
