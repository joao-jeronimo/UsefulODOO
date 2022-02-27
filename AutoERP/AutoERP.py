#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, argparse, subprocess, inspect
import autoerp_lib

ALL_OPER_MODES = []
def opermode(func):
    # Subcommand name:
    subcommand_name = func.__name__.replace('_', '-')
    # Build a parser for this subcommand:
    function_args = list(inspect.signature(func).parameters)
    subparser_args = []
    for this_arg in function_args:
        subparser_args.append(
            dict(
                #name       = opmode[0],
                #dest        = opmode[0],
                #required    = False,
                #default     = None,
                
                dest        = this_arg,
                action      = 'store',
                type        = str,
                #action      = 'store_const',
                #const       = opmode[1],
                #help        = opmode[2],
                ) )
    # Add command to list:
    ALL_OPER_MODES.append(
        (subcommand_name, func, func.__doc__, subparser_args, )
        )
    return func

def read_manifest(manifest_path):
    with open(manifest_path, "r") as manifile:
        manifcontents = manifile.read()
    return eval(manifcontents)

def create_suite_folders(suitename):
    subprocess.check_output([
        "mkdir",
        "-p",
        os.path.join(os.path.sep, "odoo", "Suites", suitename),
        ])
    subprocess.check_output([
        "mkdir",
        "-p",
        os.path.join(os.path.sep, "odoo", "Suites", suitename, "Repos"),
        ])

def fetch_repo_to(repospec, destpath):
    #git.Repo.clone("--single-branch", "-b", repospec['branch'], repospec['url'], destpath)
    subprocess.check_output([
        "git",
        "clone",
        "--single-branch",
        "-b",
        repospec['branch'],
        repospec['url'],
        destpath,
        ])

@opermode
def fetch_suite_repos(suitename):
    """
    ** Pass 2  - Call this after creating the instance.
    """
    suitemanifest = suite_info(suitename)
    create_suite_folders(suitename)
    # Fetch the repos:
    all_suite_repos = suitemanifest['repositories']
    for this_repo in all_suite_repos:
        fetch_repo_to (c,
            this_repo,
            os.path.join(os.path.sep, "odoo", "Suites", suitename, "Repos", this_repo['localname'])
            )

@opermode
def suite_info(suitename):
    """
    Print information about a suite.
    """
    suitepath = os.path.join("Suites", suitename)
    if not os.path.isdir(suitepath):
        print("No such suite: %s"%suitename)
        exit(-1)
    manifest_data = read_manifest(os.path.join(suitepath, "__manifest__.py"))
    print(repr(manifest_data))
    return manifest_data

RELEASE_PYVER = {
    '13.0':         "3.7",
    }

@opermode
def create_instance(release_num, instancenm, httpport, private=True):
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
        listen_on               = "127.0.0.1" if private else "0.0.0.0",
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

@opermode
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
    call_makefile(c,
        python_major_version    = python_version.split('.')[0],
        python_minor_version    = python_version.split('.')[1],
        targetnames              = "prepare_virtualenv",
        )

@opermode
def get_instance_config(self, instancenm):
    inst = autoerp_lib.OdooInstance(instancenm)
    print( repr( inst.get_http_port() ) )

def main(argv):
    # See: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Auto ERP - An installer for Odoo.')
    # Operating modes are subparsers:
    subparsers  = parser.add_subparsers()
    #print("Operating modes: "+" ".join([ repr(funcd) for funcd in ALL_OPER_MODES ]) )
    for opmode in ALL_OPER_MODES:
        this_parser = subparsers.add_parser(opmode[0])
        for this_arg in opmode[3]:
            this_parser.add_argument(**this_arg)
        
        #this_parser.add_argument("number", type=int)
        
        #kw_arg_spec = dict(
        #    #name       = opmode[0],
        #    #dest        = opmode[0],
        #    #required    = False,
        #    #default     = None,
        #    
        #    #action      = 'store_const',
        #    const       = opmode[1],
        #    help        = opmode[2],
        #    )
        #print("Adding operating mode: %s" % ( repr(kw_arg_spec), ) )
        
    args = parser.parse_args()
    print(args)

if __name__ == "__main__": main(sys.argv)