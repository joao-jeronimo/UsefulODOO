#!/usr/bin/python3
# -*- coding: utf8 -*-
import pudb
import os
import socket
from data import *
from taskman import *
from odootasks import *

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
            (odoobranch, instance_name, httpport) = parts[1:]
            mainTaskMan.scheduleTask(OdooSetupDatabase(MAIN_GIT_LOCAL_REPO, odoobranch, instance_name, httpport, ODOO_USERNAME ))
            return ("Setting-up Odoo-%s instance '%s'." % (odoobranch, instance_name), "Done!")
        if parts[0] == "startinstance":
            pass
        if parts[0] == "stopinstance":
            pass
        if parts[0] == "nginxconfig":
            (httpport, hostname) = parts[1:]
            mainTaskMan.scheduleTask(OdooNginxConfig(httpport, hostname ))
            return ("Configuring NGinx for website %s on port %s." % (hostname, httpport), "Done!")
        else:
            return ("Invalid command.",)
    except (IndexError, ValueError):
        return ("Invalid syntax.",)

def sendBack(conn, response):
    conn['connsocket'][0].send(response.encode())

def main():
    global mainTaskMan
    mainTaskMan = TaskMan()
    # Scheduling and running basic tasks:
    mainTaskMan.scheduleTask(OdooMkDirs())
    mainTaskMan.scheduleTask(OdooProcConfig())
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
            try:
                sendBack(connection, commandresult[0]+"\n")
            except BrokenPipeError:
                # I we cannot deliver response back to client, don't do the command.
                print("Command aborted due to broken pipe.")
                continue
            #pudb.set_trace()
            mainTaskMan.taskMan_main()
            try:
                if len(commandresult) > 1:
                    sendBack(connection, commandresult[1]+"\n")
            except BrokenPipeError:
                # Client may not be interested in knowing that the command has ended, so ignore is pipe is broken.
                pass
    finally:
        print("Releasing the connection...")
        tearDownNetwork(connection)

if __name__ == '__main__': main()
