#!/usr/bin/python3
# -*- coding: utf8 -*-

import os
from taskman import *

MAIN_GIT_REMOTE_REPO    = "https://github.com/odoo/odoo.git"
MAIN_GIT_LOCAL_REPO     = "/odoo/odoo-full-git/"


class OdooMkDirs(Task):
    def __init__(self):
        pass
    def run(self, taskman):
        dirslist = ("/odoo/", "/odoo/configs/", "/odoo/logs/")
        for thedir in dirslist:
            try:
                os.mkdir(thedir)
            except FileExistsError:
                pass
class OdooFetch(Task):
    def __init__(self, gitpath):
        self.gitpath = gitpath
    def taskReqs(self):
        return ['OdooMkDirs']
    def run(self, taskman):
        # Main ODOO source:
        os.chdir("/odoo/")
        if not self.gitcloned():
            proclib.runprog_shareout(["git", "clone", MAIN_GIT_REMOTE_REPO, MAIN_GIT_LOCAL_REPO])
    # Auxiliary functions:
    def gitcloned(self):
        return os.path.isdir(MAIN_GIT_LOCAL_REPO)

def main():
    mainTaskMan = TaskMan()
    # Scheduling and running basic tasks:
    mainTaskMan.scheduleTask(OdooMkDirs())
    mainTaskMan.scheduleTask(OdooFetch(MAIN_GIT_REMOTE_REPO))
    mainTaskMan.taskMan_main()
    # Initializing server:
    # TODO

if __name__ == '__main__': main()
