import os
from invoke import task
# Call this file with:
#invoke --list

def read_manifest(manifest_path):
    with open(manifest_path, "r") as manifile:
        manifcontents = manifile.read()
    return eval(manifcontents)
    
@task
def suite_info(c, suitename):
    suitepath = os.path.join("Suites", suitename)
    if not os.path.isdir(suitepath):
        print("No such suite: %s"%suitename)
        exit(-1)
    manifest_data = read_manifest(os.path.join(suitepath, "__manifest__.py"))
    print(repr(manifest_data))

RELEASE_PYVER = {
    '13.0':         "3.7",
    }

@task
def create_instance(c, release_num, instancenm, httpport, private=True):
    if release_num in RELEASE_PYVER.keys(): python_version = RELEASE_PYVER[release_num]
    else:                                   python_version = "3.7"
    # A list of targets to run:
    TARGETS_TO_RUN = [
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
        instance_modfolders     = "/odoo/custom/xpto",
        pythonlibs_dir          = "/odoo/PythonLibs",
        targetname              = " ".join(TARGETS_TO_RUN),
        )
    # Run all the needed targets:
    call_makefile(c, **makefile_params)

@task
def install_release(c, release_num):
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
        instance_modfolders     = "/odoo/custom/xpto",
        pythonlibs_dir          = "/odoo/PythonLibs",
        targetname              = " ".join(TARGETS_TO_RUN),
        )
    # Run all the needed targets:
    call_makefile(c, **makefile_params)

@task
def call_makefile(c,    odoo_rel="", instancenm="", listen_on="0.0.0.0", httpport="8999",
                        wkhtmltopdf_version="0.12.6-1", debian_codename="buster", python_major_version="3", python_minor_version="7",
                        instance_modfolders="", pythonlibs_dir="",
                        targetname="prepare_all" ):
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
    c.run(  'sudo --preserve-env=%(make_vars_list)s make -f Odoo.makefile %(targetname)s' % {
                    'make_vars_list':   make_vars_list,
                    'targetname':       targetname,
                    },
            env = make_vars,
            )

@task
def prepare_virtualenv(c, python_version="3.7"):
    call_makefile(c,
        python_major_version    = python_version.split('.')[0],
        python_minor_version    = python_version.split('.')[1],
        targetname              = "prepare_virtualenv",
        )
