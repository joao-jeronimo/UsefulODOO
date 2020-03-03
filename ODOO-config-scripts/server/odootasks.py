#!/usr/bin/python3
# -*- coding: utf8 -*-
import pudb
import os
import proclib
from taskman import *
from data import *

safe_eval = eval

class OdooTask(Task):
    # Auxiliary functions:
    def systemd_file_exists(self, instance_name):
        return os.path.isfile(self.systemd_file_path(instance_name))
    def systemd_file_path(self, instance_name):
        return ("/lib/systemd/system/odoo-%s.service"%instance_name)
    
    def branchcloned(self, thebranch):
        return os.path.isdir(self.branch_path(thebranch))
    def branch_path(self, thebranch):
        return "/odoo/releases/odoo-b%s/"%(thebranch,)
    
    def configfile_exists(self, instance_name):
        return os.path.isfile(self.odoo_configfile_path(instance_name))
    def odoo_configfile_path(self, instance_name):
        return ("/odoo/configs/odoo-%s.conf"%instance_name)
    
    def nginx_file_exists(self, hostname):
        return os.path.isfile(self.nginx_vhost_file_path(hostname))
    def nginx_vhost_file_path(self, hostname):
        return ("/etc/nginx/sites-available/%s"%hostname)
    
    def nginx_symlink_exists(self, hostname):
        return os.path.islink(self.nginx_vhost_symlink_path(hostname))
    def nginx_vhost_symlink_path(self, hostname):
        return ("/etc/nginx/sites-enabled/%s"%hostname)

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

class OdooProcConfig(OdooTask):
    def __init__(self):
        pass
    def run(self, taskman):
        if not os.path.isfile(SCRIPTCONFIG):
            scriptconfigfile_obj = open(SCRIPTCONFIG, "w")
            scriptconfigfile_obj.write("{'DB_PASSWORD': ''}")
            scriptconfigfile_obj.close()
        scriptconfigfile_obj = open(SCRIPTCONFIG, "r")
        scriptconfigfile_contents = scriptconfigfile_obj.read()
        scriptconfigfile_obj.close()
        config_dikt = safe_eval(scriptconfigfile_contents)
        
        global DB_PASSWORD
        DB_PASSWORD = config_dikt['DB_PASSWORD']

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
    def __init__(self, localgitpath, odoobranch, instance_name, httpport, odoo_username):
        self.localgitpath = localgitpath
        self.odoobranch = odoobranch
        self.instance_name = instance_name
        self.httpport = httpport
        self.odoo_username = odoo_username
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch']
    def run(self, taskman):
        print("Setting up instance '%s'..."%(self.instance_name))
        taskman.scheduleChildTask(OdooCloneBranch(self.localgitpath, self.odoobranch))
        taskman.scheduleChildTask(OdooInstallBranchDeps(self.odoobranch))
        taskman.scheduleChildTask(OdooCreateConfig(self.odoobranch, self.instance_name, self.httpport, self.odoo_username))
        taskman.scheduleChildTask(OdooSystemdConfig(self.odoobranch, self.instance_name, self.odoo_username))

class OdooCloneBranch(OdooTask):
    def __init__(self, localgitpath, odoobranch):
        self.localgitpath = localgitpath
        self.odoobranch = odoobranch
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch', 'OdooSetupDatabase']
    def run(self, taskman):
        if self.branchcloned(self.odoobranch):
            return
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
        os.chdir(self.branch_path(self.odoobranch))
        proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "--upgrade", "pip"])   #TODO: Move this line to earlier tasks:
        proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "-r", "requirements.txt"])

class OdooCreateConfig(OdooTask):
    def __init__(self, odoobranch, instance_name, httpport, odoo_username):
        self.odoobranch = odoobranch
        self.instance_name = instance_name
        self.httpport = httpport
        self.odoo_username = odoo_username
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch',
                'OdooSetupDatabase', 'OdooCloneBranch', 'OdooInstallBranchDeps']
    def run(self, taskman):
        if self.configfile_exists(self.instance_name):
            return
        configfile_concrete = ODOO_CONFIGFILE_TEMPLATE % {  
                        'branchpath': self.branch_path(self.odoobranch),
                        'instancename': self.instance_name,
                        'httpport': self.httpport,
                        'odoo_username': self.odoo_username,
                        }
        configfile_obj = open(self.odoo_configfile_path(self.instance_name), "w")
        configfile_obj.write(configfile_concrete)
        configfile_obj.close()

class OdooSystemdConfig(OdooTask):
    def __init__(self, odoobranch, instance_name, odoo_username):
        self.odoobranch = odoobranch
        self.instance_name = instance_name
        self.odoo_username = odoo_username
    def taskReqs(self):
        return ['OdooMkDirs', 'OdooFetch',
                'OdooSetupDatabase', 'OdooCloneBranch', 'OdooInstallBranchDeps', 'OdooCreateConfig']
    def run(self, taskman):
        if self.systemd_file_exists(self.instance_name):
            return
        systemdfile_concrete = SYSTEMD_FILE_TEMPLATE % {
                        'branchpath': self.branch_path(self.odoobranch),
                        'instancename': self.instance_name,
                        'odoo_username': self.odoo_username,
                        }
        systemdfile_obj = open(self.systemd_file_path(self.instance_name), "w")
        systemdfile_obj.write(systemdfile_concrete)
        systemdfile_obj.close()

###########################################
### Setting-uo Nginx virtual host:
class OdooNginxConfig(OdooTask):
    def __init__(self, httpport, hostname):
        self.httpport = httpport
        self.hostname = hostname
    def taskReqs(self):
        return []
    def run(self, taskman):
        taskman.scheduleChildTask(OdooNginxConfigFile(self.httpport, self.hostname))
        taskman.scheduleChildTask(OdooNginxActivate(self.hostname))
        taskman.scheduleChildTask(OdooNginxReload(self.hostname))

class OdooNginxConfigFile(OdooTask):
    def __init__(self, httpport, hostname):
        self.httpport = httpport
        self.hostname = hostname
    def taskReqs(self):
        return []
    def run(self, taskman):
        if self.nginx_file_exists(self.hostname):
            return
        nginx_file_concrete = NGINX_FILE_TEMPLATE % {
                        'httpport': self.httpport,
                        'hostname': self.hostname,
                        }
        nginx_file_obj = open(self.nginx_vhost_file_path(self.hostname), "w")
        nginx_file_obj.write(nginx_file_concrete)
        nginx_file_obj.close()

class OdooNginxActivate(OdooTask):
    def __init__(self, hostname):
        self.hostname = hostname
    def taskReqs(self):
        return ['OdooNginxConfig']
    def run(self, taskman):
        if self.nginx_symlink_exists(self.hostname):
            return
        os.symlink(
            self.nginx_vhost_file_path(self.hostname),
            self.nginx_vhost_symlink_path(self.hostname)
            )

class OdooNginxReload(OdooTask):
    def __init__(self, hostname):
        self.hostname = hostname
    def taskReqs(self):
        return ['OdooNginxConfig', 'OdooNginxActivate']
    def run(self, taskman):
        proclib.runprog_shareout(["systemctl", "restart", "nginx"])
