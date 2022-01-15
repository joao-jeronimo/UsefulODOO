from invoke import task
# Call this file with:
#invoke --list

@task
def install_release(c, release_num):
    pass

@task
def call_makefile(c,    odoo_rel, instancenm, httpport, listen_on,
                        wkhtmltopdf_version, debian_codename, python_version,
                        instance_modfolders, pythonlibs_dir):
    # Vars dictionary:
    make_vars = {
        'ODOO_REL'              : odoo_rel,
        'INSTANCENM'            : instancenm,
        'HTTPPORT'              : httpport,
        'WKHTMLTOPDF_VERSION'   : wkhtmltopdf_version,
        'DEBIAN_CODENAME'       : debian_codename,
        'LISTEN_ON'             : listen_on,
        'INSTANCE_MODFOLDERS'   : instance_modfolders,
        'PYTHON_VERSION'        : python_version,
        'PYTHONLIBS_DIR'        : pythonlibs_dir,
        }
    # Convert dictionary to arguments:
    make_vars_list = ",".join(make_vars.keys())
    #with c.run(""):
    # Run the makefile twice:
    c.run(  'sudo --preserve-env=%(make_vars_list)s make -f Odoo.makefile prepare_virtualenv' % {
                    'make_vars_list': make_vars_list,
                    },
            env = make_vars,
            )
    #c.run(2source /odoo/sidilcode13/%(installer_dir)s/External/LaunchScripts/0_SetupEnvironment.bash")
    c.run(  'sudo --preserve-env=%(make_vars_list)s make -f Odoo.makefile prepare_all' % {
                    'make_vars_list': make_vars_list,
                    },
            env = make_vars,
            )
