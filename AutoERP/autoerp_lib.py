import sys, os, argparse, subprocess, inspect, autoerp_lib, pdb, importlib, re
# Push "Libs" directory onto python path:
scriptdir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.join(scriptdir, "Libs")
sys.path.insert(0, libs_dir)
import util_odoo
# Import configuration file parser:
sys.path.insert(0, os.path.join( os.path.sep, "odoo", "releases", "13.0") )
odoo_config_parser = importlib.import_module( "odoo.tools.config" )

# Important constants:
ODOO_ROOT = os.path.join(os.path.sep, "odoo")
SUITE_TEMPLATE_DIR = os.path.join(os.path.curdir, "Suites")
INSTANCES_DIR = os.path.join(ODOO_ROOT, "Instances")
REPOS_SUBFOLDER_NAME = "SuiteRepos"

RELEASE_PYVER = {
    '13.0':         "3.7",
    }

class SuiteTemplate:
    def __init__(self, suitename):
        (
            self.suitename,
            ) = (
                suitename,
            )
        self.suitemanifest = self.suite_info()
    
    def _read_manifest(self, manifest_path):
        with open(manifest_path, "r") as manifile:
            manifcontents = manifile.read()
        return eval(manifcontents)
    
    def suitepath(self):
        return os.path.join(SUITE_TEMPLATE_DIR, self.suitename)
    
    def suite_info(self):
        """
        Print information about a suite.
        """
        suitepath = self.suitepath()
        if not os.path.isdir(suitepath):
            print("No such suite: %s"%self.suitename)
            exit(-1)
        manifest_data = self._read_manifest(os.path.join(suitepath, "__manifest__.py"))
        print(repr(manifest_data))
        return manifest_data
    
    def create_suite_folders(self, basedir):
        subprocess.check_output(["mkdir", "-p", os.path.join(basedir),                  ])
    
    def _fetch_repo_to(self, repospec, instance, destpath):
        if repospec['type'] == 'git':
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
        elif repospec['type'] == 'included':
            srcpath = os.path.join(self.suitepath(), (repospec['srcpath'])%{ 'odoo_rel': instance.release_num, } )
            subprocess.check_output([
                "cp",
                "-Rv",
                srcpath,
                destpath,
                ])
    
    def run_hook(self, instance, repo, hookname, basedir):
        # Get name of function to call:
        if hookname not in repo:
            return
        function_name = repo[hookname]
        # Import the suite as a python package:
        suite_package = importlib.import_module( "Suites."+self.suitename )
        # Try to get the function to call:
        hook_function = getattr(suite_package, function_name)
        # Do call it:
        hook_function(instance, repo['localname'], basedir)
    
    def fetch_prepare_suite_repos(self, instance):
        self.do_fetch_suite_repos( instance )
        self.do_prepare_suite_repos( instance )
        return self.get_module_paths( instance )
    
    def get_module_paths(self, instance):
        """
        Fetches all suite repositories, returning the resulting paths of the fetched modules.
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        # Fetch the repos, building and collecting the resulting paths for return:
        all_module_paths = []
        for this_repo in all_suite_repos:
            repo_root = os.path.join(basedir, this_repo['localname'])
            for this_modpath in this_repo['modpaths']:
                all_module_paths.append(os.path.join(repo_root, this_modpath))
        return all_module_paths
    
    def do_fetch_suite_repos(self, instance):
        """
        Fetches all suite repositories, returning the resulting paths of the fetched modules.
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        self.create_suite_folders(basedir)
        # Fetch the repos, building and collecting the resulting paths for return:
        for this_repo in all_suite_repos:
            repo_root = os.path.join(basedir, this_repo['localname'])
            self._fetch_repo_to ( this_repo, instance, repo_root )
    
    def do_prepare_suite_repos(self, instance):
        """
        Run all post-fetch hooks:
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        # Fetch the repos, building and collecting the resulting paths for return:
        for this_repo in all_suite_repos:
            # Run the post-fetch hook for this repository:
            self.run_hook(instance, this_repo, "post_fetch_hook", basedir)

class OdooInstance:
    def __init__(self, instancename, release_num=None, suitename=None, admin_password="admin"):
        (
            self.instancename,
            self.release_num,
            self.suitename,
            self.admin_password,
            ) = (
                instancename,
                release_num,
                suitename,
                admin_password,
            )
        self.parse_config_file()
        # Fill-in holes:
        if release_num is None:
            #addons_path = self.cfgman.get('addons_path')
            self.release_num = self.find_odoo_release()
        if suitename is None:
            self.suitename = self.find_suitename()
        # Instanciate the suite of the instance:
        self.suite = autoerp_lib.SuiteTemplate(self.suitename)
    
    ### Getting paths:
    def config_file_path(self):
        return os.path.join(os.path.sep, 'odoo', 'configs', 'odoo-%s.conf' % (self.instancename,), )
    def instance_conf_file_path(self):
        return os.path.join(self.get_instance_folder_path(), "instance.conf")
    def get_instance_folder_path(self):
        return os.path.join(autoerp_lib.INSTANCES_DIR, self.instancename)
    def get_instance_repos_path(self):
        return os.path.join(self.get_instance_folder_path(), REPOS_SUBFOLDER_NAME)
    def get_instance_systemd_file_path(self):
        return os.path.join(os.path.sep, 'lib', 'systemd', 'system', 'odoo-%s.service' % (self.instancename,), )
    def get_instance_logfile_path(self):
        return os.path.join(os.path.sep, 'odoo', 'logs', 'odoo-%s.log' % (self.instancename,), )
    
    ### Parsing files:
    def parse_config_file(self):
        file_path = self.config_file_path()
        print("Parsing config file %s" % (file_path,))
        self.cfgman = odoo_config_parser.configmanager(file_path)
        return self.cfgman
    def parse_instance_conf_file(self):
        instanceconf_filepath = self.instance_conf_file_path()
        self.instance_confs = {}
        with open(instanceconf_filepath, "r") as inst_config_file:
            for lin in inst_config_file:
                confpair = lin.split("=")
                self.instance_confs[confpair[0].strip()] = confpair[1].strip()
        return self.instance_confs
    def find_odoo_release(self):
        systemd_file = self.get_instance_systemd_file_path()
        with open(systemd_file, "r") as sysd_file:
            for lin in sysd_file:
                odoobin_matches = re.match(".*/odoo/releases/([0-9.]+)/odoo-bin", lin, flags=0)
                #pdb.set_trace()
                if odoobin_matches is not None:
                    return odoobin_matches[1]
    def find_suitename(self):
        self.parse_instance_conf_file()
        return self.instance_confs['suitename']
    
    ## High-level methods:
    def get_http_port(self):
        cfgman = self.parse_config_file()
        httpport = cfgman.get('http_port')
        return httpport
    
    def get_odoo_connection_params(self, username, user_id):
        conn_parms = {
            'hostname'  : 'localhost',
            'port'      : self.get_http_port(),
            'protocol'  : 'jsonrpc',
            'database'  : self.instancename,
            'login'     : username,
            'user_id'   : user_id,
            }
        if username=='admin' and self.admin_password:
            conn_parms.update({
                'password'  : self.admin_password,
                })
        return conn_parms
    
    def get_communicator(self, username="admin", user_id=2):
        return util_odoo.OdooCommunicator(self.get_odoo_connection_params(username, user_id))
    
    #################################################################################
    ### Bootstrap & Startup logic: ##################################################
    #################################################################################
    def _call_makefile(self, odoo_rel="", instancenm="", listen_on="0.0.0.0", httpport="8999",
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
    
    def _lowlevel_install_debian_deps(self, python_major_version, python_minor_version, debian=True):
        # Add needed repositories and update package tree:
        subprocess.check_output([ "sudo", "apt-get", "update", ])
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "software-properties-common", ])
        if debian:
            subprocess.check_output([ "sudo", "add-apt-repository", "contrib", ])
            subprocess.check_output([ "sudo", "add-apt-repository", "non-free", ])
        subprocess.check_output([ "sudo", "apt-get", "update", ])
        # Install python, pip, venv and other python dependencies:
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "python"+str(python_major_version), ])
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "python"+str(python_major_version)+"-pip", ])
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "python"+str(python_major_version)+"."+str(python_minor_version)+"-venv", ])
        # Install packages needed for building some wheels:
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "libffi-dev", ])
        # Install other Odoo deb-based dependencies:
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "postgresql", "postgresql-client", ])
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "ttf-mscorefonts-installer", "fonts-lato", "node-less", ])
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "libpq-dev", "libjpeg-dev", "libxml2-dev", "libxslt-dev", "zlib1g-dev", ])
        subprocess.check_output([ "sudo", "apt-get", "install", "build-dep", "-y", "python3-ldap", "python3-lxml", "python3-greenlet", ])
        # Install git and other misc stuff:
        subprocess.check_output([ "sudo", "apt-get", "install", "-y", "git", ])
    
    def _lowlevel_install_wkhtmltopdf(self):
        """
        @wget -c https://github.com/wkhtmltopdf/packaging/releases/download/$(WKHTMLTOPDF_VERSION)/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb -O ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb
        @dpkg -i ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb || true
        @apt-get --fix-broken install -y
        @touch $@
        """
        pass
    def _lowlevel_install_python_deps(self, python_major_version, python_minor_version):
        """
        sudo -H pip3 install --upgrade pip
        # Force install PortgreSQL API (psycopg2) from source:
        source $(VIRTUALENV_PATH)/bin/activate && pip3 install --ignore-installed --no-binary :all: psycopg2
        """
        pass
    
    def _lowlevel_create_instance(self, httpport, instance_modfolders, private):
        # Process args:
        python_major_version    = python_version.split('.')[0]
        python_minor_version    = python_version.split('.')[1]
        # Install/upgrade required Debian and Python dependencies:
        self._lowlevel_install_debian_deps(python_major_version, python_minor_version)
        self._lowlevel_install_wkhtmltopdf()
        self._lowlevel_install_python_deps(python_major_version, python_minor_version)
        # A list of targets to run:
        TARGETS_TO_RUN = [
            "prepare_virtualenv",
            "prepare_all",
            ]
        # Prepare parameters:
        makefile_params = dict(
            instancenm              = self.instancename,
            httpport                = httpport,
            listen_on               = "127.0.0.1" if private==1 else "0.0.0.0",
            odoo_rel                = self.release_num,
            wkhtmltopdf_version     = "0.12.6-1",
            debian_codename         = "buster",
            python_major_version    = python_major_version,
            python_minor_version    = python_minor_version,
            instance_modfolders     = ",".join(instance_modfolders),
            pythonlibs_dir          = "/odoo/PythonLibs",
            targetnames             = " ".join(TARGETS_TO_RUN),
            )
        # Run all the needed targets:
        self._call_makefile(**makefile_params)
    
    def create_instance(self, httpport, instance_modfolders, private):
        if self.release_num in RELEASE_PYVER.keys(): python_version = RELEASE_PYVER[self.release_num]
        else:                                   python_version = "3.7"
        self._lowlevel_create_instance(httpport, instance_modfolders, private)
    
    def install_suite(self, httpport, private):
        """
        Does a full suite install if it is not already installed.
        """
        subprocess.check_output(["mkdir", "-p", self.get_instance_folder_path(), ])
        # Spawn the suite and fetch repos:
        all_modulepaths = self.suite.fetch_prepare_suite_repos(self)
        # Create the instance:
        self.create_instance(httpport, all_modulepaths, private)
        # Create instance config folder and file:
        with open(os.path.join(self.get_instance_folder_path(), "instance.conf"), "w") as inst_config_file:
            inst_config_file.write("suitename = %s" % self.suitename)
    
    def purge_instance(self, keep_code=False):
        self.stop_instance()
        subprocess.check_output(['sudo', 'rm', '-rf', self.config_file_path()])
        subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_systemd_file_path()])
        subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_logfile_path()])
        if not keep_code:
            subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_folder_path()])
    
    def start_instance(self):
        subprocess.run(['sudo', 'systemctl', 'start', 'odoo-%s'%self.instancename])
    def stop_instance(self):
        subprocess.run(['sudo', 'systemctl', 'stop', 'odoo-%s'%self.instancename])
    def restart_instance(self):
        subprocess.run(['sudo', 'systemctl', 'restart', 'odoo-%s'%self.instancename])
    
    def install_all_apps(self):
        thecomm = self.get_communicator()
        thecomm.wait_for_instance_ready()
        thecomm.update_modules_list()
        suitemanifest = self.suite.suite_info()
        for appspec in suitemanifest['modules']:
            if appspec['active']:
                thecomm.install_module(appspec['name'])

class NginxInstance:
    def __init__(self, odoo_instance):
        pass
    def _lowlevel_install_debian_deps(self):
        """
        apt-get update
        apt-get install -y nginx
        """
        pass
