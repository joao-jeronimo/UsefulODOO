import os
from PythonPorter import PythonPorter

def port_app(basedir, app_name_camelcase, target_name):
    print("Porting app %s to Odoo %s" % (app_name_camelcase, target_name,))
    format_names = {
        'basedir'               : basedir,
        'app_name_camelcase'    : app_name_camelcase,
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
    { 'name': "DemoModules",                                'exclude_rels': [] },
    { 'name': "FollowMouse",                                'exclude_rels': [] },
    { 'name': "DynamicAttachments",                         'exclude_rels': [] },
    { 'name': "TesseractOcrWrapper",                        'exclude_rels': [] },
    ]

def port_modules_odoo(instance, repo_localname, basedir):
    # Find out Odoo release of the instance:
    odoo_release = instance.release_num
    repo_dir = os.path.join(basedir, repo_localname)
    # Port each app:
    for app in APPS_TO_PORT:
        if odoo_release not in app['exclude_rels']:
            port_app(repo_dir, app['name'], odoo_release)
