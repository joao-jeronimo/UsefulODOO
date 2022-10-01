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
PYVENV_BIN = "pyvenv"
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
            if not os.path.isdir(destpath):
                subprocess.check_output([
                    "git",
                    "clone",
                    "--single-branch",
                    "-b",
                    repospec['branch'],
                    repospec['url'],
                    destpath,
                    ])
            else:
                previous_wd = os.getcwd()
                os.chdir(destpath)
                subprocess.check_output([
                    "git",
                    "pull",
                    ])
                os.chdir(previous_wd)
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
        Gets a list of suite repositories module paths.
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        # Fetch the repos, building and collecting the resulting paths for return:
        all_module_paths = []
        for this_repo in all_suite_repos:
            if instance.release_num in this_repo['odoo_releases']:
                repo_root = os.path.join(basedir, this_repo['localname'])
                for this_modpath in this_repo['modpaths']:
                    this_modpath = (this_modpath % { 'odoo_rel': instance.release_num, })
                    all_module_paths.append(os.path.join(repo_root, this_modpath))
        return all_module_paths
    
    def do_fetch_suite_repos(self, instance):
        """
        Fetches suite repositories, one by one.
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        self.create_suite_folders(basedir)
        # Fetch the repos, building and collecting the resulting paths for return:
        for this_repo in all_suite_repos:
            if instance.release_num in this_repo['odoo_releases']:
                repo_root = os.path.join(basedir, this_repo['localname'])
                self._fetch_repo_to ( this_repo, instance, repo_root )
    
    def do_prepare_suite_repos(self, instance):
        """
        Run all post-fetch hooks.
        """
        all_suite_repos = self.suitemanifest['repositories']
        basedir = instance.get_instance_repos_path()
        # Fetch the repos, building and collecting the resulting paths for return:
        for this_repo in all_suite_repos:
            if instance.release_num in this_repo['odoo_releases']:
                # Run the post-fetch hook for this repository:
                self.run_hook(instance, this_repo, "post_fetch_hook", basedir)

####################################################################################
##### Wrapping Commmand Execution:     #############################################
####################################################################################
class AbstractCommandRunner:
    def __init__(self, systemPythonPath, venvPythonPath):
        (self.systemPythonPath, self.venvPythonPath, ) = (
            systemPythonPath, venvPythonPath, )
    def runCommand(self, args, **kwargs):
        raise NotImplementedError("Run command «%s»: Not implemented in abstract class.")
    
    def apt_update(self):
        self.runCommand([ "sudo", "apt-get", "update", ])
    def dpkg_list(self):
        list_results = self.runCommand([ "dpkg", "-l", ], stdout=subprocess.PIPE).stdout
        linez = str(list_results).split("\n")
        # Find the ====== separator:
        list_start_lin = 0
        while len([ cr for cr in linez[list_start_lin] if cr=='=' ]) < 10:
            list_start_lin += 1
        list_start_lin += 1
        return [
            ln.split()[1]
            for ln in linez[list_start_lin:]
            ]
    
    def install_or_upgrade_apt_packages(self, packagelist):
        self.runCommand([ "sudo", "apt-get", "install", "-y", *packagelist, ])
    def install_or_upgrade_apt_build_deps(self, packagelist):
        self.runCommand([ "sudo", "apt-get", "build-dep", "-y", *packagelist, ])
    def install_or_upgrade_system_pip_package(self, packagelist):
        self.runCommand([ "sudo", "-H", self.systemPythonPath, "-m", "pip", "install", "--upgrade", *packagelist, ])
    def install_or_upgrade_venv_pip_package(self, packagelist):
        self.runCommand([ self.venvPythonPath, "-m", "pip", "install", "--upgrade", *packagelist, ])
class LocalCommandRunner(AbstractCommandRunner):
    def runCommand(self, args, **kwargs):
        return subprocess.run(args, check=True, **kwargs)

####################################################################################
##### Modeling Odoo Intances:     ##################################################
####################################################################################
class InstanceSpec:
    def __init__(self, instancename):
        (
            self.instancename,
            ) = (
                instancename,
            )
    ### Getting instance paths that depend only on the name:
    def get_instance_folder_path(self):
        return os.path.join(autoerp_lib.INSTANCES_DIR, self.instancename)
    def instance_conf_file_path(self):
        return os.path.join(self.get_instance_folder_path(), "instance.conf")
    def config_file_path(self):
        return os.path.join(os.path.sep, 'odoo', 'configs', 'odoo-%s.conf' % (self.instancename,), )
    def get_instance_repos_path(self):
        return os.path.join(self.get_instance_folder_path(), REPOS_SUBFOLDER_NAME)
    def get_instance_systemd_file_path(self):
        return os.path.join(os.path.sep, 'lib', 'systemd', 'system', 'odoo-%s.service' % (self.instancename,), )
    def get_instance_logfile_path(self):
        return os.path.join(os.path.sep, 'odoo', 'logs', 'odoo-%s.log' % (self.instancename,), )
    ### Getting instance paths that depend on other attributes:
    def get_venv_path(self):
        return os.path.join(os.path.sep, "odoo", "VirtualEnvs", self.get_venv_name())
    def get_venv_python(self):
        return os.path.join(self.get_venv_path(), "bin", "python")
    def get_venv_name(self):
        return "Env_Python" + self.get_python_version() + "_Odoo" + self.release_num
    ### Getting other important information about the instance:
    def get_python_version(self):
        if self.release_num in RELEASE_PYVER.keys():
            return RELEASE_PYVER[self.release_num]
        else:
            return "3.7"

class InstanceInstaller(InstanceSpec):
    def __init__(self, instancename, release_num, suitename, httpport, private):
        # Initialize immediate vars:
        ( self.release_num, self.httpport, self.private, ) = (
            release_num, httpport, private, )
        # Call super:
        InstanceSpec.__init__(self, instancename)
        # Instanciate the suite of the instance:
        self.suite = autoerp_lib.SuiteTemplate(suitename)
        self.executor = LocalCommandRunner("/bin/python3", self.get_venv_python())
    
    def get_installed_instance(self, skip_os_preparation):
        self.create_instance(skip_os_preparation)
        return OdooInstance(self.instancename)
    
    def create_instance(self, skip_os_preparation):
        """
        Does a full suite install if it is not already installed.
        """
        python_version = self.get_python_version()
        # Suite part:
        subprocess.check_output(["mkdir", "-p", self.get_instance_folder_path(), ])
        # Spawn the suite and fetch repos:
        all_modulepaths = self.suite.fetch_prepare_suite_repos(self)
        self._lowlevel_create_instance(self.httpport, all_modulepaths, self.private, skip_os_preparation)
        # Create instance config folder and file:
        with open(os.path.join(self.get_instance_folder_path(), "instance.conf"), "w") as inst_config_file:
            inst_config_file.write("suitename = %s" % self.suite.suitename)
    
    def _call_makefile(self, odoo_rel="", instancenm="", listen_on="0.0.0.0", httpport="8999",
                            wkhtmltopdf_version="0.12.6-1", debian_codename="buster", python_major_version="3", python_minor_version="7",
                            instance_modfolders="", pythonlibs_dir="",
                            targetnames="prepare_all" ):
        # Vars dictionary:
        make_vars = {
            'ODOO_REL'              : odoo_rel,
            'INSTANCENM'            : instancenm,
            'WITHOUT_DEMO'          : "False" if instancenm.endswith("demodevel") else "True",
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
    
    def _lowlevel_install_debian_deps(self, python_major_version, python_minor_version, debian=False):
        # Add needed repositories and update package tree:
        self.executor.apt_update()
        self.executor.install_or_upgrade_apt_packages([ "software-properties-common", ])
        if debian:
            self.executor.runCommand([ "sudo", "add-apt-repository", "contrib", ])
            self.executor.runCommand([ "sudo", "add-apt-repository", "non-free", ])
        self.executor.apt_update()
        # Install python, pip, venv and other python dependencies:
        self.executor.install_or_upgrade_apt_packages([ "python"+str(python_major_version), ])
        self.executor.install_or_upgrade_apt_packages([ "python"+str(python_major_version)+"-pip", ])
        self.executor.install_or_upgrade_apt_packages([ "python"+str(python_major_version)+"."+str(python_minor_version)+"-venv", ])
        # Install packages needed for building some wheels:
        self.executor.install_or_upgrade_apt_packages([ "libffi-dev", ])
        # Install other Odoo deb-based dependencies:
        self.executor.install_or_upgrade_apt_packages([ "postgresql", "postgresql-client", ])
        self.executor.install_or_upgrade_apt_packages([ "ttf-mscorefonts-installer", "fonts-lato", "node-less", ])
        self.executor.install_or_upgrade_apt_packages([ "libpq-dev", "libjpeg-dev", "libxml2-dev", "libxslt-dev", "zlib1g-dev", ])
        self.executor.install_or_upgrade_apt_build_deps([ "python3-ldap", "python3-lxml", "python3-greenlet", ])
        # Install git and other misc stuff:
        self.executor.install_or_upgrade_apt_packages([ "git", "screenie", ])
    
    def _lowlevel_install_wkhtmltopdf(self, version, debian_codename):
        """
        @wget -c https://github.com/wkhtmltopdf/packaging/releases/download/$(WKHTMLTOPDF_VERSION)/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb -O ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb
        @dpkg -i ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb || true
        @apt-get --fix-broken install -y
        @touch $@
        """
        if 'wkhtmltox' not in self.executor.dpkg_list():
            print("Skipping WkHtmlToX installation - already installed.")
            return
        params_dict = {
            'version':              version,
            'debian_codename':      debian_codename,
            }
        srcurl = "https://github.com/wkhtmltopdf/packaging/releases/download/%(version)s/wkhtmltox_%(version)s.%(debian_codename)s_amd64.deb" % params_dict
        destfile = "/tmp/wkhtmltox_%(version)s.%(debian_codename)s_amd64.deb" % params_dict
        # Get deb file:
        if not os.path.isfile(destfile):
            self.executor.runCommand([ "sudo", "wget", "-c", srcurl, "-O", destfile, ])
        self.executor.runCommand([ "sudo", "dpkg", "-i", destfile, ])
        self.executor.runCommand([ "sudo", "apt-get", "--fix-broken", "install", "-y" ])
    
    def _lowlevel_create_virtual_env(self, python_major_version, python_minor_version, odoo_rel):
        virtualenv_name = "Env_Python%(pymajor)s.%(pyminor)s_Odoo%(odoo_rel)s" % {
            'pymajor'      : python_major_version,
            'pyminor'      : python_minor_version,
            'odoo_rel'      : odoo_rel,
            }
        virtualenv_path = os.path.join(ODOO_ROOT, "VirtualEnvs", virtualenv_name)
        # Do the installation:
        #self.executor.runCommand([
        #    PYVENV_BIN,
        #    "--python=/usr/bin/python%(pymajor)d.%(pyminor)d" % { 'pymajor' : python_major_version, 'pyminor' : python_minor_version, },
        #    virtualenv_path,
        #    ])
        print("Virtual environment path: " + virtualenv_path)
        if not os.path.isdir(virtualenv_path):
            self.executor.runCommand([
                "python%(pymajor)s.%(pyminor)s" % { 'pymajor' : python_major_version, 'pyminor' : python_minor_version, },
                "-m", "venv",
                virtualenv_path,
                ])
    
    def _lowlevel_install_python_deps(self, python_major_version, python_minor_version):
        self.executor.install_or_upgrade_system_pip_package([ "pip", "wheel", ])
        self.executor.install_or_upgrade_venv_pip_package([ "wheel", ])
        #self.executor.runCommand([ "sudo", "pip3", "install", "--ignore-installed", "--no-binary", ":all:", "psycopg2", ])
        self.executor.runCommand([ "sudo", "pip3", "install", "psycopg2", ])
    
    def _lowlevel_create_instance(self, httpport, instance_modfolders, private, skip_os_preparation):
        #pdb.set_trace()
        # Process args:
        python_version = self.get_python_version()
        python_major_version    = python_version.split('.')[0]
        python_minor_version    = python_version.split('.')[1]
        print("================================================================")
        print("=== Install/upgrade required Debian dependencies:         ======")
        print("================================================================")
        if skip_os_preparation:
            print("(skipped)")
        else:
            self._lowlevel_install_debian_deps(python_major_version, python_minor_version)
        print("========================================")
        print("=== Installing WkHtmlToX:         ======")
        print("========================================")
        #self._lowlevel_install_wkhtmltopdf("0.12.6-1", "buster")
        self._lowlevel_install_wkhtmltopdf("0.12.6-1", "focal")
        print("========================================")
        print("=== Creating virtual environment: ======")
        print("========================================")
        self._lowlevel_create_virtual_env(python_major_version, python_minor_version, self.release_num)
        print("==================================================")
        print("=== Installing Python dependencies via pip: ======")
        print("==================================================")
        self._lowlevel_install_python_deps(python_major_version, python_minor_version)
        print("=========================================")
        print("=== Odoo instance creation proper: ======")
        print("=========================================")
        # A list of targets to run:
        TARGETS_TO_RUN = [
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
            )
        for onetarget in TARGETS_TO_RUN:
            # Run all the needed targets:
            self._call_makefile(**{
                **makefile_params,
                },
                targetnames = onetarget,
                )
    
    def purge_instance(self, keep_code=False):
        self.stop_instance()
        subprocess.check_output(['sudo', 'rm', '-rf', self.config_file_path()])
        subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_systemd_file_path()])
        subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_logfile_path()])
        if not keep_code:
            subprocess.check_output(['sudo', 'rm', '-rf', self.get_instance_folder_path()])

class OdooInstance(InstanceSpec):
    def __init__(self, instancename, admin_password="admin"):
        def find_odoo_release():
            systemd_file = self.get_instance_systemd_file_path()
            with open(systemd_file, "r") as sysd_file:
                for lin in sysd_file:
                    odoobin_matches = re.match(".*/odoo/releases/([0-9.]+)/odoo-bin", lin, flags=0)
                    #pdb.set_trace()
                    if odoobin_matches is not None:
                        return odoobin_matches[1]
        def find_suitename():
            self.parse_instance_conf_file()
            return self.instance_confs['suitename']
        # Call super:
        InstanceSpec.__init__(self, instancename)
        self.release_num = find_odoo_release()
        self.suite = SuiteTemplate(find_suitename())
        # Initialize attributes:
        ( self.admin_password, ) = (
            admin_password, )
        # Fill-in holes:
        self.parse_config_file()
        self.addons_path = self.cfgman.get('addons_path')
        self.executor = LocalCommandRunner("/bin/python3", self.get_venv_python())
    
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
    
    def get_communicator(self, username="admin", user_id=False):
        if not user_id:
            if float(self.release_num) >= float("12.0"):
                user_id = 2
            else:
                user_id = 1
        return util_odoo.OdooCommunicator(self.get_odoo_connection_params(username, user_id))
    
    def start_instance(self):
        subprocess.run(['sudo', 'systemctl', 'start', 'odoo-%s'%self.instancename])
    def stop_instance(self):
        subprocess.run(['sudo', 'systemctl', 'stop', 'odoo-%s'%self.instancename])
    def restart_instance(self):
        subprocess.run(['sudo', 'systemctl', 'restart', 'odoo-%s'%self.instancename])
    
    def install_all_apps(self, always_update=False):
        thecomm = self.get_communicator()
        thecomm.wait_for_instance_ready()
        thecomm.update_modules_list()
        suitemanifest = self.suite.suite_info()
        for appspec in suitemanifest['modules']:
            if appspec['active'] == True or self.release_num in appspec['active']:
                if always_update:
                    thecomm.install_or_upgrade_module(appspec['name'])
                else:
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
