# -*- coding: utf-8 -*-
"""

pbuilder.py
-----------

This module handles the building of packages directly from the source. As there
is no libalpm interface for building packages the fastest solution was wrapping
_makepkg_ to accomplish automated building of packages.
"""

import os, sys
import shutil
import tarfile
import urllib
from StringIO import StringIO
from subprocess import Popen, PIPE, STDOUT, call
from time import sleep
import signal

from item import PackageItem, AURPackageItem
from events import Events
from tools import CriticalError

class BuildError(CriticalError):
    pass

class PackageBuilder(object):
    """Manages the building process

    :param session: a :class:`pyalpmm.Session` instance
    :param pkg_obj: the :class:`PackageItem` to build
    """
    def __init__(self, session, pkg_obj):
        self.session = session
        self.events = session.config.events
        self.pkg = pkg_obj
        self.path = os.path.join(
            self.session.config.build_dir,
            pkg_obj.repo,
            pkg_obj.name
        )
        self.pkgfile_path = None

    def cleanup(self):
        """Delete (without complaining if not found) the complete target package
        build directory and all its subdirectories
        """
        shutil.rmtree(self.path, True)
        self.events.DoneBuildDirectoryCleanup()

    def prepare(self):
        """Prepare means:

        * decide if we have a AUR or ABS package to build
        * download the required scripts to build
        """

        c = self.session.config
        if isinstance(self.pkg, PackageItem):
            self.events.StartABSBuildPrepare()

            # cleanup abs (deleting old builds in abs here - is this good??)
            abs_path = os.path.join(c.abs_dir, self.pkg.repo, self.pkg.name)
            shutil.rmtree(abs_path, True)

            # get PKGBUILD and co
            if not os.system("abs %s/%s" % (self.pkg.repo, self.pkg.name)) == 0:
                raise BuildError("Could not successfuly execute 'abs'")

            shutil.copytree(abs_path, self.path)
        elif isinstance(self.pkg, AURPackageItem):
            self.events.StartAURBuildPrepare()

            # get and extract
            url = c.aur_url + c.aur_pkg_dir + self.pkg.name + "/" + \
                self.pkg.name + ".tar.gz"
            # we hold the whole thing in RAM, hmm FIXME
            to = tarfile.open(fileobj=StringIO(urllib.urlopen(url).read()))
            to.extractall(os.path.dirname(self.path))
            to.close()
        else:
            raise BuildError(("The passed pkg was not an instance of "
                              "(AUR)PackageItem, more a '{0}'").format(
                              type(pkg_obj).__name__))

        self.events.DoneBuildPrepare()

    def build(self):
        """Building is done with the given uid inside a fork,
        only if PKGBUILD is found and we can change into the directory.
        If successful, set self.pkgfile_path to built package
        """

        self.events.StartBuild(pkg=self.pkg)
        c = self.session.config

        if not os.path.exists(os.path.join(self.path, "PKGBUILD")):
            raise BuildError("PKGBUILD not found at {0}".format(self.path))

        try:
            os.chdir(self.path)
        except OSError as e:
            raise BuildError("Could not change directory to: {0}".\
                             format(self.path))

        makepkg = "makepkg {1} {0}".format(
            "> /dev/null 2>&1" if c.build_quiet else "",
            "-f" if c.force else ""
        ).strip()

        # if run as root, setuid to other user
        if os.getuid() == 0:
            os.chown(self.path, c.build_uid, c.build_gid)
            recv, send = os.pipe()
            pid = os.fork()
            if pid == 0:
                os.close(recv)
                os.setuid(c.build_uid)
                ret = str(call(makepkg.split(" ")))
                send = os.fdopen(send, "w")
                send.write(ret)
                send.close()
                sys.exit(0)
            else:
                os.close(send)
                recv = os.fdopen(recv)
                ret = recv.read()
                os.waitpid(pid, 0)
                recv.close()

                if ret != "0":
                    raise BuildError("The build failed with the makepkg "
                           "returncode: {0}".format(ret))
        else:
            raise BuildError("you are not root!")

        self.events.DoneBuild()

        # kinda ugly
        for fn in os.listdir(self.path):
            if fn.endswith(c.pkg_suffix):
                self.pkgfile_path = os.path.join(self.path, fn)
                break

        if self.pkgfile_path is None:
            raise BuildError("The package file could not be found, "
                             "maybe check the build-dir: {0}".format(self.path))

    # TODO: this maybe should callback so you could have a gui editor easily
    def edit(self):
        """Edit the PKGBUILD with an editor invoked by 'editor_command'"""

        self.events.StartBuildEdit()

        if os.system("%s %s" % (
            self.session.config.editor_command,
            os.path.join(self.path, "PKGBUILD")
        )) != 0:
            raise BuildError("Editor returned error, aborting build")

        self.events.DoneBuildEdit()