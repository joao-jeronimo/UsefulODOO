import sys, os, importlib
# Push "Libs" directory onto python path:
scriptdir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.join(scriptdir, "Libs")
sys.path.insert(0, libs_dir)
import util_odoo
# Import configuration file parser:
sys.path.insert(0, os.path.join( os.path.sep, "odoo", "releases", "13.0") )
odoo_config_parser = importlib.import_module( "odoo.tools.config" )

class OdooInstance:
    def __init__(self, instacename):
        (
            self.instacename,
            ) = (
                instacename,
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
