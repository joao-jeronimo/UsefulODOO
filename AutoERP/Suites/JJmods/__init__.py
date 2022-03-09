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

def port_modules_odoo(instance, repo_localname, basedir):
    # Find out Odoo release of the instance:
    odoo_release = instance.release_num
    repo_dir = os.path.join(basedir, repo_localname)
    # Port each app:
    port_app(repo_dir, "payslip_aggregate_rule", odoo_release)
    port_app(repo_dir, "payroll_typesafe_formulas", odoo_release)
    port_app(repo_dir, "alternative_detailed_payslip", odoo_release)
    
    port_app(repo_dir, "payslip_advanced_info_tab", odoo_release)
    port_app(repo_dir, "payslip_effective_dates", odoo_release)
    port_app(repo_dir, "payslip_proportional_bases", odoo_release)
