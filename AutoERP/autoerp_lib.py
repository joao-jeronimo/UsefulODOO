import sys, os, argparse, subprocess, inspect, autoerp_lib, pdb, importlib
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

class SuiteTemplate:
    def __init__(self, suitename):
        (
            self.suitename,
            ) = (
                suitename,
            )
    
    def _read_manifest(self, manifest_path):
        with open(manifest_path, "r") as manifile:
            manifcontents = manifile.read()
        return eval(manifcontents)
    
    def suite_info(self):
        """
        Print information about a suite.
        """
        suitepath = os.path.join(SUITE_TEMPLATE_DIR, self.suitename)
        if not os.path.isdir(suitepath):
            print("No such suite: %s"%self.suitename)
            exit(-1)
        manifest_data = self._read_manifest(os.path.join(suitepath, "__manifest__.py"))
        print(repr(manifest_data))
        return manifest_data
    
    def create_suite_folders(self, basedir):
        subprocess.check_output(["mkdir", "-p", os.path.join(basedir),                  ])
        subprocess.check_output(["mkdir", "-p", os.path.join(basedir, "SuiteRepos"),    ])
    
    def _fetch_repo_to(self, repospec, destpath):
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
    
    def fetch_suite_repos(self, basedir):
        suitemanifest = self.suite_info()
        self.create_suite_folders(basedir)
        # Fetch the repos:
        all_suite_repos = suitemanifest['repositories']
        for this_repo in all_suite_repos:
            self._fetch_repo_to (
                this_repo,
                os.path.join(basedir, this_repo['localname'])
                )

class OdooInstance:
    def __init__(self, instacename, suitename=None):
        (
            self.instacename,
            self.suitename,
            ) = (
                instacename,
                suitename,
            )
    
    ### Getting paths:
    def config_file_path(self):
        return os.path.join(
            os.path.sep,
            'odoo',
            'configs',
            'odoo-%s.conf' % (self.instacename,),
            )
    
    ### Parsing files:
    def parse_config_file(self):
        file_path = self.config_file_path()
        print("Parsing config file %s" % (file_path,))
        cfgman = odoo_config_parser.configmanager(file_path)
        return cfgman
    
    ## High-level methods:
    def get_http_port(self):
        cfgman = self.parse_config_file()
        httpport = cfgman.get('http_port')
        return httpport
    
    def get_odoo_connection_params(self, username, user_id):
        return {
            'hostname'  : 'localhost',
            'port'      : self.get_http_port(),
            'protocol'  : 'jsonrpc',
            'database'  : self.instacename,
            'login'     : username,
            'user_id'   : user_id,
            }
    
    def get_communicator(self, username="admin", user_id=2):
        return util_odoo.OdooCommunicator(self.get_odoo_connection_params(username, user_id))
