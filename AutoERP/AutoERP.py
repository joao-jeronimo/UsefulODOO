#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, argparse, subprocess, inspect, autoerp_lib, pdb

# Collectiong subcommands:
ALL_OPER_MODES = []
def opermode(func):
    # Subcommand name:
    subcommand_name = func.__name__.replace('_', '-')
    # Build a parser for this subcommand:
    function_sign = inspect.signature(func)
    function_arg_keys = list(function_sign.parameters)
    #function_sign.parameters['python_version'].default
    #pdb.set_trace()
    subparser_args = []
    for this_arg in function_arg_keys:
        arg_default = function_sign.parameters[this_arg].default
        
        subparser_args.append(
            dict(
                dest        = this_arg,
                action      = 'store',
                type        = str,
                
                #name       = opmode[0],
                #dest        = opmode[0],
                #action      = 'store_const',
                #const       = opmode[1],
                #help        = opmode[2],
                
                # Absent arguments with comments of why they are absent:
                #required    = False,           # TypeError: 'required' is an invalid argument for positionals.
                #default     = arg_default,     # All arguments are mandatory for now, so there are no defaults.
                ) )
    # Add command to list:
    ALL_OPER_MODES.append(
        {
            'subcommand_name':      subcommand_name,
            'func':                 func,
            'function_docstring':   func.__doc__,
            'function_args':        function_arg_keys,
            'subparser_args':       subparser_args,
            }
        )
    return func

@opermode
def suite_info(suitename):
    """
    Print information about a suite.
    """
    suite = SuiteTemplate(suitename)
    suite.suite_info()



@opermode
def create_instance(release_num, instancenm, httpport, private):
    """
    ** Pass 1  - Call this first, then fetch_suite_repos
    """
    inst = autoerp_lib.OdooInstance(instancenm, release_num)
    inst.create_instance(httpport, private)

@opermode
def install_suite(release_num, instancenm, httpport, suitename, private):
    inst = autoerp_lib.OdooInstance(instancenm, release_num, suitename)
    inst.install_suite(httpport, private)

@opermode
def full_launch_instance(release_num, instancenm, httpport, suitename, private):
    inst = autoerp_lib.OdooInstance(instancenm, release_num, suitename)
    inst.install_suite(httpport, private)
    inst.start_instance()
    inst.install_all_apps()

@opermode
def purge_instance(instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    inst.purge_instance()

@opermode
def get_instance_config(instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    print( repr( inst.get_http_port() ) )

def do_update_module(instancenm, module_name, fast=False):
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
    thecomm.install_or_upgrade_module(module_name)

@opermode
def update_module(instancenm, module_name):
    do_update_module(instancenm, module_name, fast=False)
@opermode
def update_module_fast(instancenm, module_name):
    do_update_module(instancenm, module_name, fast=True)

@opermode
def activate_demo_data(instancenm):
    if not instancenm.endswith("devel"):
        print("Demo data can only be loaded in databases whose name ends in 'devel'.")
        exit(-1)
    inst = autoerp_lib.OdooInstance(instancenm)
    comm = inst.get_communicator()
    demo_model = comm.odoo_connection.get_model('ir.demo')
    demo_model.install_demo(False)

def main(argv):
    # See: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Auto ERP - An installer for Odoo.')
    # Operating modes are subparsers (add_subparsers() method only enables subparsers feature):
    subparsers  = parser.add_subparsers()
    #print("Operating modes: "+" ".join([ repr(funcd) for funcd in ALL_OPER_MODES ]) )
    for opmode in ALL_OPER_MODES:
        this_subparser = subparsers.add_parser(opmode['subcommand_name'])
        # Add subcommand arguments, the same way that top-level arguments would
        # be added, but add them to the subparser instead:
        for this_arg in opmode['subparser_args']:
            this_subparser.add_argument(**this_arg)
        # Add the function that ought to be called when this subcommand is called. This is
        # done via set_defaults:
        this_subparser.set_defaults(func=opmode['func'])
    
    # Parse full comand line, then print arguments:
    args = parser.parse_args()
    print(args)
    # Get list of arguments of the fcuntion that we need to call:
    function_args = list(inspect.signature(args.func).parameters)
    # Create dictionary that only contains the function-spacific commands:
    args_to_subcommand = dict([
        (func_arg, getattr(args, func_arg))
        for func_arg in function_args
        if func_arg in dir(args)
        ])
    # Call the command function:
    args.func(**args_to_subcommand)

if __name__ == "__main__": main(sys.argv)
