#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, argparse, subprocess, inspect, pdb
import autoerp_lib, cmdline

@cmdline.opermode
def suite_info(suitename):
    """
    Print information about a suite.
    """
    suite = SuiteTemplate(suitename)
    suite.suite_info()



@cmdline.opermode
def create_instance(instancenm, release_num, httpport, suitename, private):
    """
    ** Pass 1  - Call this first, then fetch_suite_repos
    """
    installer = autoerp_lib.InstanceInstaller(instancenm, release_num, suitename, httpport, private)
    inst = installer.get_installed_instance()
    inst.create_instance()

@cmdline.opermode
def full_launch_instance(instancenm, release_num, httpport, suitename, private):
    inst = autoerp_lib.OdooInstance(instancenm, release_num, suitename)
    inst.start_instance()
    inst.install_all_apps()

@cmdline.opermode
def purge_instance(instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    inst.purge_instance()

@cmdline.opermode
def get_instance_config(instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    print( repr( inst.get_http_port() ) )

def do_update_module(instancenm, module_name, fast=False, reinstall=False):
    inst = autoerp_lib.OdooInstance(instancenm)
    # Re-run post-fetch hooks for each repository:
    inst.suite.do_prepare_suite_repos(inst)
    # Restart deamon:
    if not fast:
        inst.restart_instance()
    # Call upgrade:
    thecomm = inst.get_communicator()
    thecomm.wait_for_instance_ready()
    thecomm.update_modules_list()
    if reinstall:
        thecomm.safe_uninstall_module(module_name)
    thecomm.install_or_upgrade_module(module_name)

@cmdline.opermode
def update_module(instancenm, module_name):
    do_update_module(instancenm, module_name, fast=False)
@cmdline.opermode
def update_module_fast(instancenm, module_name):
    do_update_module(instancenm, module_name, fast=True)
@cmdline.opermode
def update_module_unsafe(instancenm, module_name):
    do_update_module(instancenm, module_name, fast=False, reinstall=True)

@cmdline.opermode
def activate_demo_data(instancenm):
    if not instancenm.endswith("devel"):
        print("Demo data can only be loaded in databases whose name ends in 'devel'.")
        exit(-1)
    inst = autoerp_lib.OdooInstance(instancenm)
    comm = inst.get_communicator()
    demo_model = comm.odoo_connection.get_model('ir.demo')
    demo_model.install_demo(False)

###############################################
def main(argv):
    cmdline.parse_and_do(argv)
if __name__ == "__main__": main(sys.argv)
