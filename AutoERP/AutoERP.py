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

RELEASE_PYVER = {
    '13.0':         "3.7",
    }

@opermode
def create_instance(release_num, instancenm, httpport, private):
    """
    ** Pass 1  - Call this first, then fetch_suite_repos
    """
    if release_num in RELEASE_PYVER.keys(): python_version = RELEASE_PYVER[release_num]
    else:                                   python_version = "3.7"
    # A list of targets to run:
    TARGETS_TO_RUN = [
        "prepare_virtualenv",
        "prepare_all",
        ]
    # Prepara parameters:
    makefile_params = dict(
        instancenm              = instancenm,
        httpport                = httpport,
        listen_on               = "127.0.0.1" if private==1 else "0.0.0.0",
        odoo_rel                = release_num,
        wkhtmltopdf_version     = "0.12.6-1",
        debian_codename         = "buster",
        python_major_version    = python_version.split('.')[0],
        python_minor_version    = python_version.split('.')[1],
        instance_modfolders     = os.path.join(os.path.sep, "odoo", ("custom_%s"%release_num)),
        pythonlibs_dir          = "/odoo/PythonLibs",
        targetnames             = " ".join(TARGETS_TO_RUN),
        )
    # Run all the needed targets:
    call_makefile(**makefile_params)

@opermode
def install_suite(release_num, instancenm, httpport, suitename, private):
    instance_folder = os.path.join(autoerp_lib.INSTANCES_DIR, instancenm)
    subprocess.check_output(["mkdir", "-p", instance_folder, ])
    # Spawn the suite and fetch repos:
    suite = autoerp_lib.SuiteTemplate(suitename)
    suite.fetch_suite_repos(os.path.join(instance_folder, "SuiteRepos"))
    # Create the instance:
    create_instance(release_num, instancenm, httpport, private)
    # Create instance config folder and file:
    with open(os.path.join(instance_folder, "instance.conf"), "w") as inst_config_file:
        inst_config_file.write("suitename = %s" % suitename)

@opermode
def install_release(release_num):
    if release_num in RELEASE_PYVER.keys(): python_version = RELEASE_PYVER[release_num]
    else:                                   python_version = "3.7"
    # A list of targets to run:
    TARGETS_TO_RUN = [
        "/odoo/stages/dep_branch_requirements",
        "/odoo/stages/dep_wkhtmltopdf",
        "/odoo/stages/system_user_created",
        "/odoo/logs",
        "/odoo/releases/%s"%(release_num),
        "/odoo/stages/sql_user_created",
        ]
    # Prepara parameters:
    makefile_params = dict(
        #instancenm              = "",
        #httpport                = "",
        #listen_on               = "",
        odoo_rel                = release_num,
        wkhtmltopdf_version     = "0.12.6-1",
        debian_codename         = "buster",
        python_major_version    = python_version.split('.')[0],
        python_minor_version    = python_version.split('.')[1],
        instance_modfolders     = os.path.join(os.path.sep, "odoo", ("custom_%s"%release_num)),
        pythonlibs_dir          = "/odoo/PythonLibs",
        targetnames             = " ".join(TARGETS_TO_RUN),
        )
    # Run all the needed targets:
    call_makefile(**makefile_params)

def call_makefile(   odoo_rel="", instancenm="", listen_on="0.0.0.0", httpport="8999",
                        wkhtmltopdf_version="0.12.6-1", debian_codename="buster", python_major_version="3", python_minor_version="7",
                        instance_modfolders="", pythonlibs_dir="",
                        targetnames="prepare_all" ):
    # Vars dictionary:
    make_vars = {
        'ODOO_REL'              : odoo_rel,
        'INSTANCENM'            : instancenm,
        'LISTEN_ON'             : listen_on,
        'HTTPPORT'              : httpport,
        'WKHTMLTOPDF_VERSION'   : wkhtmltopdf_version,
        'INSTANCE_MODFOLDERS'   : instance_modfolders,
        'PYTHON_MAJOR_VERSION'  : python_major_version,
        'PYTHON_MINOR_VERSION'  : python_minor_version,
        'PYTHONLIBS_DIR'        : pythonlibs_dir,
        
        'DEBIAN_CODENAME'       : debian_codename,
        'DISTRO'                : "ubuntu",
        }
    # Convert dictionary to arguments:
    make_vars_list = ",".join(make_vars.keys())
    # Do call the makefile:
    subprocess.check_output([
        "sudo",
        "--preserve-env=%(make_vars_list)s" % { 'make_vars_list':   make_vars_list, },
        "make", "-f", "Odoo.makefile",
        *( targetnames.split(" ") ),
        ],
        env = make_vars,
        )

@opermode
def prepare_virtualenv(python_version="3.7"):
    call_makefile(
        python_major_version    = python_version.split('.')[0],
        python_minor_version    = python_version.split('.')[1],
        targetnames              = "prepare_virtualenv",
        )

@opermode
def get_instance_config(instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    print( repr( inst.get_http_port() ) )

@opermode
def install_module(instancenm, module_name):
    inst = autoerp_lib.OdooInstance(instancenm)
    comm = inst.get_communicator()
    comm.install_module(module_name)

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