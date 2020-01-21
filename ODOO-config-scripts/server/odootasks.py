#!/usr/bin/python3
# -*- coding: utf8 -*-
import pudb
import os
import proclib
from taskman import *

class OdooTask(Task):
    # Auxiliary functions:
    def systemd_file_path(self, instance_name):
        return ("/lib/systemd/system/odoo-%s.service"%instance_name)
    def systemd_file_exists(self):
        return os.path.isfile(self.systemd_file_path(self.instance_name))
    def branchcloned(self):
        return os.path.isdir(self.branch_path(self.odoobranch))
    def branch_path(self, thebranch):
        return "/odoo/releases/odoo-b%s/"%(thebranch,)
    def configfile_exists(self):
        return os.path.isdir(self.odoo_configfile_path(self.odoobranch))
    def odoo_configfile_path(self, instance_name):
        return ("/odoo/configs/odoo-%s.conf"%instance_name)

class OdooMkDirs(OdooTask):
    def __init__(self):
        pass
    def run(self, taskman):
        dirslist = ("/odoo/", "/odoo/configs/", "/odoo/logs/")
        for thedir in dirslist:
            try:
                os.mkdir(thedir)
            except FileExistsError:
                pass

class OdooFetch(OdooTask):
    def __init__(self, remotegitpath, localgitpath):
        self.remotegitpath = remotegitpath
        self.localgitpath = localgitpath
    def taskReqs(self):
        return ['OdooMkDirs']
    def run(self, taskman):
        # Main ODOO source:
        os.chdir("/odoo/")
        if not self.gitcloned():
            proclib.runprog_shareout(["git", "clone", self.remotegitpath, self.localgitpath])
    # Auxiliary functions:
    def gitcloned(self):
        return os.path.isdir(self.localgitpath)

###########################################
### Database setup main task - with childreen:
class OdooSetupDatabase(OdooTask):
    def __init__(self, localgitpath, odoobranch, instance_name):
        self.localgitpath = localgitpath
        self.odoobranch = odoobranch
        self.instance_name = instance_name
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch']
    def run(self, taskman):
        print("Setting up instance '%s'..."%(self.instance_name))
        if not self.branchcloned():
            taskman.scheduleChildTask(OdooCloneBranch(self.localgitpath, self.odoobranch))
            taskman.scheduleChildTask(OdooInstallBranchDeps(self.odoobranch))
        if not self.configfile_exists():
            taskman.scheduleChildTask(OdooCreateConfig(self.odoobranch, self.instance_name))
        if not self.systemd_file_exists():
            taskman.scheduleChildTask(OdooSystemdConfig(self.odoobranch, self.instance_name))

class OdooCloneBranch(OdooTask):
    def __init__(self, localgitpath, odoobranch):
        self.localgitpath = localgitpath
        self.odoobranch = odoobranch
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch', 'OdooSetupDatabase']
    def run(self, taskman):
        print("Cloning branch %s..."%(self.odoobranch))
        os.chdir(self.localgitpath)
        proclib.runprog_shareout(["git", "checkout", self.odoobranch])
        proclib.runprog_shareout(["git", "pull"])
        
        commlist = ["git", "clone", "-b", self.odoobranch, "--single-branch", self.localgitpath, self.branch_path(self.odoobranch)]
        print ("Running: %s" % (str(commlist),) )
        proclib.runprog_shareout(commlist)

class OdooInstallBranchDeps(OdooTask):
    def __init__(self, odoobranch):
        self.odoobranch = odoobranch
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch',
                'OdooSetupDatabase', 'OdooCloneBranch']
    def run(self, taskman):
        pass

class OdooCreateConfig(OdooTask):
    def __init__(self, odoobranch, instance_name):
        self.odoobranch = odoobranch
        self.instance_name = instance_name
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch',
                'OdooSetupDatabase', 'OdooCloneBranch', 'OdooInstallBranchDeps']
    def run(self, taskman):
        pass

class OdooSystemdConfig(OdooTask):
    def __init__(self, odoobranch, instance_name):
        self.odoobranch = odoobranch
        self.instance_name = instance_name
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch',
                'OdooSetupDatabase', 'OdooCloneBranch', 'OdooInstallBranchDeps', 'OdooCreateConfig']
    def run(self, taskman):
        pass

