import sys, os, importlib
sys.path.insert(0, os.path.join( os.path.sep, "odoo", "releases", "13.0") )
odoo_config_parser = importlib.import_module( "odoo.tools.config" )
#import odoo.tools.config

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
