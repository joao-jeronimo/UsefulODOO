import os
from PythonPorter import PythonPorter

def snakecase2cammelcase(str_in_snake):
    splitted = str_in_snake.split("_")
    return "".join([ word.capitalize() for word in splitted ])

def port_app(basedir, app_name_snakecase, target_name):
    print("Porting app %s to Odoo %s" % (app_name_snakecase, target_name,))
    format_names = {
        'basedir'               : basedir,
        'app_name_snakecase'    : app_name_snakecase,
        'app_name_camelcase'    : snakecase2cammelcase(app_name_snakecase),
        'target_name'           : target_name,
        }
    # Params:
    macrodir = "%(basedir)s/%(app_name_camelcase)s/Targets/%(target_name)s" % format_names
    srcdir   = "%(basedir)s/%(app_name_camelcase)s/Src"                     % format_names
    dstdir   = "%(basedir)s/0_Installable/%(target_name)s"                  % format_names
    # Run porter for app and release:
    pporter = PythonPorter(macrodir, srcdir, dstdir)
    pporter.load_macros()
    pporter.do_preprocess_directory()

APPS_TO_PORT = [
    { 'name': "payslip_advanced_info_tab",          'exclude_rels': ['11.0', '12.0', '13.0', ] },
    
    { 'name': "payslip_aggregate_rule",             'exclude_rels': [] },
    { 'name': "payroll_typesafe_formulas",          'exclude_rels': [] },
    
    { 'name': "payslip_effective_dates",            'exclude_rels': ['11.0', '12.0', '13.0', ] },
    { 'name': "payslip_proportional_bases",         'exclude_rels': ['11.0', '12.0', '13.0', ] },
    
    { 'name': "alternative_detailed_payslip",       'exclude_rels': ['11.0', '12.0', '13.0',  ] },
    { 'name': "simple_payslip_template",            'exclude_rels': [] },
    
    { 'name': "hr_payroll_community_demo_data",     'exclude_rels': [] },
    ]

def port_modules_odoo(instance, repo_localname, basedir):
    # Find out Odoo release of the instance:
    odoo_release = instance.release_num
    repo_dir = os.path.join(basedir, repo_localname)
    # Port each app:
    for app in APPS_TO_PORT:
        if odoo_release not in app['exclude_rels']:
            port_app(repo_dir, app['name'], odoo_release)
