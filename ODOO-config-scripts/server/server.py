#!/usr/bin/python3
# -*- coding: utf8 -*-

import os
import socket
from taskman import *
from odootasks import *

MAIN_GIT_REMOTE_REPO    = "https://github.com/odoo/odoo.git"
MAIN_GIT_LOCAL_REPO     = "/odoo/odoo-full-git/"

def setupNetwork(address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, port))
    s.listen(1)
    return {
        'origsocket':   s,
        'connsocket':   None    # (conn, addr)
        }

def tearDownNetwork(connection):
    connection['origsocket'].close()

def waitForCommand(connection):
    while True:
        if connection['connsocket'] == None:
            connection['connsocket'] = connection['origsocket'].accept()
            connection['asfile'] = connection['connsocket'][0].makefile()
        retline = connection['asfile'].readline()
        # Black line is terminating the connection. Accept another one, then! Empty lines otherwise are returned as "\n".
        if not retline:
            connection['connsocket'][0].close()
            connection['connsocket'] = None
            connection['asfile'] = None
        else:
            return retline

def intrCommand(command):
    parts = command.split()
    try:
        if parts[0] == "setupinstance":
            return "Setting-up Odoo-%s instance '%s'." % (parts[1], parts[2],)
            mainTaskMan.scheduleTask(OdooSetupDatabase(parts[1], parts[2], ))
        if parts[0] == "startinstance":
            pass
        if parts[0] == "stopinstance":
            pass
        if parts[0] == "nginxconfig":
            pass
    except IndexError:
        return "Invalid syntax"

def sendBack(conn, response):
    conn['connsocket'][0].send(response.encode())

def main():
    global mainTaskMan
    mainTaskMan = TaskMan()
    # Scheduling and running basic tasks:
    mainTaskMan.scheduleTask(OdooMkDirs())
    mainTaskMan.scheduleTask(OdooFetch(MAIN_GIT_REMOTE_REPO, MAIN_GIT_LOCAL_REPO))
    mainTaskMan.taskMan_main()
    # Launching network:
    connection = setupNetwork("127.0.0.1", 10000)
    try:
        # Network command loop - this is supposed to be single-threaded!
        while True:
            command = waitForCommand(connection).strip()
            if command == "stopserver":
                mainTaskMan.saveTaskList()
                tearDownNetwork(connection)
                break
            commandresult = intrCommand(command)
            sendBack(connection, commandresult)
    finally:
        tearDownNetwork(connection)

if __name__ == '__main__': main()
