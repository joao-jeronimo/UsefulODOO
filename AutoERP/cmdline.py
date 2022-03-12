# -*- coding: utf-8 -*-
import sys, os, argparse, subprocess, inspect, autoerp_lib, pdb

# Collecting subcommands:
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

def parse_and_do(argv):
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
