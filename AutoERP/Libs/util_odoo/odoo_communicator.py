#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Version 1 - Start phasing-out util_odoo.py

import sys, os, io, time, datetime, odoolib, tempfile, re, base64, ezodf, random, string
from odoo_csv_tools import import_threaded
from odoo_csv_tools.lib.internal.csv_reader import UnicodeReader, UnicodeWriter
from getpass import getpass
from unidecode import unidecode as remove_accents
import http.client
if sys.version_info >= (3, 0, 0):
    import configparser as ConfigParser
else:
    import ConfigParser
import pdb

##########################################################
#### Useful constants: ###################################
##########################################################
SUPERUSER_LOGIN = '__system__'
SUPERUSER_UID = 1

N_TRIALS    = 20
WAIT_SECS   = 7

def prepare_config(hostname, port, protocol, database, login, user_id):
    return {
        'hostname'  : hostname,
        'port'      : port,
        'protocol'  : protocol,
        'database'  : database,
        'login'     : login,
        'user_id'   : user_id,
        }

#######################################################################
### Usefull functions: ################################################
#######################################################################
# Some constants:
nw = datetime.datetime.now()
last_month_end = datetime.datetime(year=nw.year, month=nw.month, day=1)-datetime.timedelta(1)
last_month_start = datetime.datetime(year=last_month_end.year, month=last_month_end.month, day=1)

def gen_random_password(length):
    choosable_chars = string.printable
    #choosable_chars = string.ascii_lowercase
    result_str = ''.join(random.choice(choosable_chars) for i in range(length))
    return result_str

#######################################################################
def csv_read_file(file_to_read, delimiter=';', encoding='utf-8', skip=0):
    def is_string(f):
        if sys.version_info >= (3, 0, 0):
            return isinstance(f, str)
        else:
            return isinstance(f, basestring)
    
    def open_read(f, encoding='utf-8'):
        if not is_string(f):
            return f
        if sys.version_info >= (3, 0, 0):
            return open(f, 'r', newline='', encoding=encoding)
        else:
            return open(f, 'r')
    
    def get_real_header(header):
        """ Get real header cut at the first empty column """
        new_header = []
        for head in header:
            if head:
                new_header.append(head)
            else:
                break
        return new_header

    def skip_line(reader):
        print("Skipping until line %s excluded" % skip)
        for _ in range(1, skip):
            reader.next()

    print('open %s' % file_to_read)
    file_ref = open_read(file_to_read, encoding=encoding)
    reader = UnicodeReader(file_ref, delimiter=delimiter, encoding=encoding)
    header = next(reader)
    header = get_real_header(header)
    skip_line(reader)
    data = [l for l in reader]
    return header, data

def check_id_column(header):
    try:
        header.index('id')
    except ValueError as ve:
        log_error("No External Id (id) column defined, please add one")
        raise ve

def convert_date(datestring):
    try:
        if datestring=="" or datestring==None: return None
        
        if isinstance(datestring, str):
            datestring=datestring.strip()
            datestuffs = datestring.split("/")
            ano=int(datestuffs[2])
            mes=int(datestuffs[1])
            dia=int(datestuffs[0])
        else:
            dateobject = datestring
            ano = dateobject.year
            mes = dateobject.month
            dia = dateobject.day
        
        return "%04d-%02d-%02d"%(ano, mes, dia)
    except Exception as be:
        print ("Falhou na data: " + str(datestring) )
        raise be

def convert_date_comparable(datestring):
    try:
        datestring=datestring.strip()
        if datestring=="" or datestring==None: return None
        
        datestuffs = datestring.split("/")
        ano=int(datestuffs[2])
        mes=int(datestuffs[1])
        dia=int(datestuffs[0])
        
        import datetime
        return datetime.datetime(year=ano, month=mes, day=dia)
    except Exception as be:
        print ("Falhou na data: " + str(datestring) )
        raise be

def copy_dikt_fields(thefrom, theto, thefields):
    for i in thefields:
        if type(i)==tuple:  dstnm = i[1] ; srcnm = i[0]
        else:               dstnm = i ; srcnm = i
        theto[dstnm] = thefrom[srcnm].strip()

def copy_dikt_fields_defaultdates(thefrom, theto, thefields):
    for i in thefields:
        if type(i)==tuple:  dstnm = i[1] ; srcnm = i[0]
        else:               dstnm = i ; srcnm = i
        if thefrom[i].strip()=='':
            theto[dstnm] = '01/01/1900'
        else:
            theto[dstnm] = convert_date(thefrom[srcnm])

def copy_dikt_fields_money(thefrom, theto, thefields):
    for i in thefields:
        if type(i)==tuple:  dstnm = i[1] ; srcnm = i[0]
        else:               dstnm = i ; srcnm = i
        theto[dstnm] = thefrom[srcnm].strip().replace(",",".")

#######################################################################
### Object-Oriented code: #############################################
#######################################################################
class OdooCommException(BaseException):
    pass

class OdooCommunicator:
    def __init__(self, connection_params, the_password=False):
        self.connection_params = connection_params
        if 'password' not in connection_params.keys() or not connection_params['password']:
            if not the_password:
                the_password = getpass("Enter '%s' (uid=%d) ODOO user password: "%(self.connection_params['login'], self.connection_params['user_id']))
            self.connection_params['password'] = the_password
        # Create the connection:
        self.reconnect()
    
    connection_context = {}
    
    def reconnect(self):
        self.odoo_connection = odoolib.get_connection(**self.connection_params)
    
    sudo_password = False
    sudo_connection_params = False
    sudo_odoo_connection = False
    
    def sudo(self):
        """
        (WARNING: THIS DOES NOT WORK!)
        Return another (possible reused) odoo connection suitable for running
        operations with superuser permissions.
        """
        if not self.sudo_odoo_connection:
            # Set a random password for uid=1 user:
            users_model = self.odoo_connection.get_model('res.users')
            if not self.sudo_password:
                self.sudo_password = gen_random_password(80)
            users_model.write(SUPERUSER_UID, {
                'password': self.sudo_password,
                #'active': True,
                } )
            # Connect using the suitable password:
            if not self.sudo_connection_params:
                self.sudo_connection_params = self.connection_params.copy()
            #pdb.set_trace()
            self.sudo_connection_params['login'] = SUPERUSER_LOGIN
            self.sudo_connection_params['user_id'] = SUPERUSER_UID
            self.sudo_connection_params['password'] = self.sudo_password
            self.sudo_odoo_connection = odoolib.get_connection(**self.sudo_connection_params)
            #pdb.set_trace()
        return self.sudo_odoo_connection
    
    ############################################################################
    ### External IDs manipulation: #############################################
    ############################################################################
    def resolve_xid(self, xid_module, xid_name):
        """
        Returns dictionary in the form {'model', model, 'res_id', res_id}
        """
        the_xid_record = self.odoo_connection.get_model("ir.model.data").search_read([
                        ('module', '=', xid_module),
                        ('name', '=', xid_name),
                        ], fields=['model', 'res_id'], limit=1)
        #print (str(the_xid_record))
        if len(the_xid_record)==1:  return the_xid_record[0]
        else:                       return {'model':False, 'res_id':False, }
    def resolve_dxid(self, dxid_name):
        return self.resolve_xid(*dxid_name.split('.'))
    def get_xid(self, modelname, res_id):
        the_xid_record = self.odoo_connection.get_model("ir.model.data").search_read([
                        ('model',   '=', modelname),
                        ('res_id',  '=', res_id),
                        ], fields=['module', 'name'], limit=1)
        #print (str(the_xid_record))
        if len(the_xid_record)==1:  return the_xid_record[0]
        else:                       return False
    def assign_xid(self, xid_module, xid_name, modelname, res_id):
        write_dikt = {
            'module'    : xid_module,
            'name'      : xid_name,
            'model'     : modelname,
            'res_id'    : res_id,
            }
        # Now patch or create the record:
        existing_xid = self.get_xid(modelname, res_id)
        if existing_xid:
            self.odoo_connection.get_model("ir.model.data").write(existing_xid['id'], write_dikt)
        else:
            self.odoo_connection.get_model("ir.model.data").create(write_dikt)
    
    def unlink_by_xid(self, xid):
        rec_info = self.resolve_dxid(xid)
        if type(rec_info['model']) is str:
            model_proxy = self.odoo_connection.get_model(rec_info['model'])
            model_proxy.unlink(rec_info['res_id'])

    ############################################################################
    ### Modules: ###############################################################
    ############################################################################
    def update_modules_list(self):
        print("# A sondar novos módulos...")
        modules_model = self.odoo_connection.get_model("base.module.update")
        #pdb.set_trace()
        wizard_instance = modules_model.create({})
        modules_model.update_module(wizard_instance)

    def give_module_op_errors_and_die(self, e):
        exc_string = str(e).replace("\\n", "\n")
        if (    exc_string.find('The server is busy right now, module operations are not possible')!=-1
                or exc_string.find('Remote end closed connection without')!=-1 ):
            print("Servidor ocupado... a tentar novamente em %d segundos." % (WAIT_SECS,))
            time.sleep(WAIT_SECS)
            return True
        else:
            print("Falhou! Traceback interno do erro:")
            print( exc_string.replace("\\n", "\n") )
            exit(-1)

    def module_state(self, techname, verbose=True):
        n_tries = 0
        retry = True
        while retry:
            try:
                n_tries += 1
                modules_model = self.odoo_connection.get_model("ir.module.module")
                themodule = modules_model.search([('name', '=', techname)])
                if not(any(themodule)):
                    print("Módulo %s não encontrado..."%techname)
                    exit(-1)
                # Fast skip if already installed:
                mod_state_before = modules_model.read(themodule, fields=['state'])
                return mod_state_before[0]['state']
            except odoolib.main.JsonRPCException as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e
            except http.client.RemoteDisconnected as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e

    def install_module(self, techname, verbose=True):
        n_tries = 0
        retry = True
        while retry:
            try:
                n_tries += 1
                if verbose:
                    print("# Instalar módulo %s ..."%techname)
                modules_model = self.odoo_connection.get_model("ir.module.module")
                themodule = modules_model.search([('name', '=', techname)])
                if not(any(themodule)):
                    print("Módulo não encontrado...")
                    exit(-1)
                # Fast skip if already installed:
                mod_state_before = modules_model.read(themodule, fields=['state'])
                if mod_state_before[0]['state'] == 'installed': return True
                modules_model.button_immediate_install(themodule)
                # See if was installed:
                mod_state_after = modules_model.read(themodule, fields=['state'])
                if mod_state_after[0]['state'] != 'installed':
                    print("Instalação falhou... ver web e ficheiro log.")
                    exit(-1)
                return
            except odoolib.main.JsonRPCException as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e
            except http.client.RemoteDisconnected as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e

    def upgrade_module(self, techname):
        n_tries = 0
        retry = True
        while retry:
            try:
                print("# A atualizar módulo %s ..."%techname)
                modules_model = self.odoo_connection.get_model("ir.module.module")
                themodule = modules_model.search([('name', '=', techname)])
                if not(any(themodule)):
                    print("Módulo não encontrado...")
                    exit(-1)
                mod_state_before = modules_model.read(themodule, fields=['state'])
                if mod_state_before[0]['state'] != 'installed':
                    print("Para ser atualizado, o módulo precisa estar o estado 'Instalado'...")
                    exit(-1)
                modules_model.button_immediate_upgrade(themodule)
                # See if was upgraded:
                mod_state_after = modules_model.read(themodule, fields=['state'])
                if mod_state_after[0]['state'] != 'installed':
                    print("Atualização falhou... verificar web e ficheiro log.")
                    exit(-1)
                return
            except odoolib.main.JsonRPCException as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e

    def install_or_upgrade_module(self, techname):
        modules_model = self.odoo_connection.get_model("ir.module.module")
        themodule = modules_model.search([('name', '=', techname)])
        if not(any(themodule)):
            print("Módulo não encontrado...")
            exit(-1)
        mod_state_before = modules_model.read(themodule, fields=['state'])
        if mod_state_before[0]['state'] == 'installed':
            self.upgrade_module(techname)
        else:
            self.install_module(techname)
    
    def get_module_id(self, techname):
        modules_model = self.odoo_connection.get_model("ir.module.module")
        themodule = modules_model.search([('name', '=', techname)])
        if not(any(themodule)):
            print("Módulo não encontrado...")
            exit(-1)
        return themodule
    
    def get_module_state(self, mod_id):
        modules_model = self.odoo_connection.get_model("ir.module.module")
        mod_state = modules_model.read(mod_id, fields=['state'])
        return mod_state[0]['state']
    
    def get_module_dependencies(self, mod_id):
        """
        Module dependencies as other modules that this moduel depends on.
        Returns a lista of [id, name] pairsof dependencies.
        """
        module_model = self.odoo_connection.get_model("ir.module.module")
        module_dependency_model = self.odoo_connection.get_model("ir.module.module.dependency")
        # Getting dependencies objects:
        mod_depobjs_readed = module_model.read(mod_id, fields=['dependencies_id'])
        mod_depobjs_ids = mod_depobjs_readed[0]['dependencies_id']
        # At this point, var mod_deps_ids contains ids for ir.module.module.dependency
        # objects. Let's resolve them:
        dep_ids = module_dependency_model.read(mod_depobjs_ids, fields=['depend_id', ])
        dep_data = [ (d['depend_id'][0], d['depend_id'][1]) for d in dep_ids ]
        return dep_data
    
    def get_module_dependants(self, mod_id):
        """
        Module dependencies as other modules that this moduel depends on.
        """
        modules_model = self.odoo_connection.get_model("ir.module.module")
        module_dependency_model = self.odoo_connection.get_model("ir.module.module.dependency")
        # Get every dependency object that points to this module:
        dependants_ids_readed = module_dependency_model.search_read([('depend_id', '=', mod_id)], fields=['module_id'])
        dependants_data = [ ( d['module_id'][0], d['module_id'][1] ) for d in dependants_ids_readed ]
        #pdb.set_trace()
        return dependants_data
    
    def assert_module_state(self, mod_id, accepted_states, errmsg):
        mod_state = self.get_module_state(mod_id)
        if mod_state not in accepted_states:
            print(errmsg)
            exit(-1)
    
    def safe_uninstall_module(self, techname, idenpotent=False):
        """
        Uninstall module, but fail if it has dependencies.
        """
        modules_model = self.odoo_connection.get_model("ir.module.module")
        self.update_modules_list()
        themodule_id = self.get_module_id(techname)
        mod_dependants_data = self.get_module_dependants(themodule_id)
        # See which deps are installed:
        installed_deps = modules_model.search_read([
            ('id', 'in', [ data[0] for data in mod_dependants_data ]),
            ('state', 'in', ['installed']),
            ], fields=['id', 'name', 'state'])
        #pdb.set_trace()
        # Give error if any:
        if any(installed_deps):
            print("Erro: Não é possível desinstalar o módulo %s pois ele tem as seguintes dependências instaladas:")
            for installed_dep in installed_deps:
                print(repr(installed_dep))
            exit(-1)
        self.uninstall_module(techname, idenpotent)

    def uninstall_module(self, techname, idenpotent=False):
        n_tries = 0
        retry = True
        while retry:
            try:
                print("# A desinstalar módulo %s..."%techname)
                modules_model = self.odoo_connection.get_model("ir.module.module")
                themodule = self.get_module_id(techname)
                if idenpotent and self.get_module_state(themodule) == 'uninstalled':
                    return
                self.assert_module_state(themodule, ['installed'], "Para ser desinstalado, o módulo precisa estar o estado 'Instalado'...")
                modules_model.button_immediate_uninstall(themodule)
                # See if was uninstalled:
                mod_state_after = modules_model.read(themodule, fields=['state'])
                if mod_state_after[0]['state'] != 'uninstalled':
                    print("Desinstalação falhou... verificar web e ficheiro log.")
                    exit(-1)
                return
            except odoolib.main.JsonRPCException as e:
                retry = self.give_module_op_errors_and_die(e)
                if retry and n_tries>=N_TRIALS: raise e
    
    def activate_chart_of_accounts_by_dxid(self, the_coa_dxid, company_id=False):
        try:
            coa_id = self.resolve_dxid(the_coa_dxid)['res_id']
            coa_template_model = self.odoo_connection.get_model("account.chart.template")
            coa_template_model.try_loading(coa_id, company_id)
        except odoolib.main.JsonRPCException as ex:
            exc_string = str(ex).replace("\\n", "\n")
            print("== Error loading COA:\n"+exc_string)
            exit(-1)
    
    ############################################################################
    ### Groups and System Parameters: ##########################################
    ############################################################################
    def put_user_in_groups(self, log_in, groups_xids):
        users_model = self.odoo_connection.get_model("res.users")
        groups_model = self.odoo_connection.get_model("res.groups")
        # Get user id:
        the_uid = users_model.search([('login', '=', log_in)])
        assert len(the_uid)==1
        for gr_xid in groups_xids:
            # Get group id:
            gr_xid_parts = gr_xid.split(".")
            gr_id = self.resolve_xid(gr_xid_parts[0], gr_xid_parts[1])['res_id']
            # Add the user (write opcode means to add existing record to the group):
            groups_model.write(gr_id, { 'users': [ (4, the_uid[0], None), ] })

    def set_system_parameter(self, parmname, parmvalue):
        sysparms_model = self.odoo_connection.get_model("ir.config_parameter")
        theobj = sysparms_model.search([('key', '=', parmname)])
        sysparms_model.write(theobj, { 'value': parmvalue })

    def set_field_defaults(self, field_dxid, json_default_value, user_login=False):
        # Get model proxies:
        ModelIrDefault = self.odoo_connection.get_model("ir.default")
        ModelModelFields = self.odoo_connection.get_model("ir.model.fields")
        ModelUsers = self.odoo_connection.get_model("res.users")
        # Find the field ID:
        field_id = self.resolve_dxid(field_dxid)['res_id']
        # Find ID of user with that login:
        if user_login:
            user_id = ModelUsers.search([('login', '=', user_login)])
        else:
            user_id = False
        # See if there is already a default definition for that field:
        existing_defaults = ModelIrDefault.search([
                ('field_id', '=', field_id),
                ('user_id', '=', user_id),
                ])
        if existing_defaults:
            existing_defaults = existing_defaults[0]
        else:
            existing_defaults = ModelIrDefault.create({
                'field_id': field_id,
                })
        # Set default value for field:
        ModelIrDefault.write(existing_defaults, {
            'json_value':   json_default_value,
            'user_id':      user_id,
            })
    
    ################################################################
    ### General Data Loads: ########################################
    ################################################################
    def gen_dict(self, model, src=[], dst='id', srcfield=False):
        #pdb.set_trace()
        if not srcfield:
            srcfield = src[0][0]
        Model = self.odoo_connection.get_model(model)
        associateable = Model.search_read(src, fields=[srcfield, dst])
        ret = {}
        for item in associateable:
            s = item[srcfield]
            d = item[dst]
            ret[s] = d
        return ret
    
    def doload(self, themodel, thefields, thedatas, context={}):
        n_trials = 0
        while True:
            try:
                n_trials += 1
                print("A carregar dados...")
                loadret = self.odoo_connection.get_model(themodel).load(thefields, thedatas, context=context)
                #print("Return da função de load: "+str(loadret))
                if loadret['ids'] == False:
                    print("============= Mass load error! =============")
                    print("loadret = "+str(loadret) )
                    raise odoolib.main.JsonRPCException(loadret)
            except odoolib.main.JsonRPCException as e:
                if 'messages' in e.args[0] and e.args[0]['messages'][0]['message'].find("busy") != -1:
                    print("Servidor ocupado... a tentar novamente em %d segundos." % (WAIT_SECS,))
                    if n_trials >= N_TRIALS: raise e
                    time.sleep(WAIT_SECS)
                else:
                    print("Falhou! Traceback interno do erro:")
                    print("thefields = "+str(thefields))
                    print("thedatas = "+str(thedatas).replace("[[", "[\n  [").replace("], [", "],\n  [").replace("]]", "]\n]") )
                    print("First error: " + str(e.args[0]).replace("\\n", "\n"))
                    exit(-1)
            return loadret

    def find_relation_model(self, modelname, fieldname):
        models_model = self.odoo_connection.get_model("ir.model")
        fields_model = self.odoo_connection.get_model("ir.model.fields")
        # Find model's id:
        model_id = models_model.search([ ('model', '=', modelname), ])
        # Field field's id:
        relat_data = fields_model.search_read(
                [ ('name', '=', fieldname), ('model_id', '=', model_id), ],
                fields=['relation'])
        if len(relat_data) == 0:
            print("!!!!! ERRO: O modelo %s não tem nenhum campo chamado %s." % (modelname, fieldname,))
            exit(-1)
        return relat_data[0]['relation']

    def cook_csv_askey(self, themodel, header, data, coli, context={}):
        # Get the field to use as key:
        key_field = re.sub("^askey:", "", header[coli], flags=0)
        all_field_values = list(set([ lin[coli] for lin in data ]))
        # Add column at the end so that new record creation works well:
        header.append(key_field)
        # Get External IDs of all records corresponding to that entries:
        model_proxy = self.odoo_connection.get_model(themodel)
        field_correspondence_context = {**context, **self.connection_context, **{'active_test': False}, }
        all_field_ids = model_proxy.search(
                [(key_field, 'in', all_field_values)],
                context=field_correspondence_context, )
        all_field_pairs = model_proxy.export_data(
                all_field_ids,
                ['id', key_field],
                context=field_correspondence_context )['datas']
        # On by one, find the id on the list that was returned by the server, and replace:
        for lini in range(len(data)):
            # Add the column's data to the new column:
            raw_data = data[lini][coli]
            data[lini].append(raw_data)
            # Find the XID and replace it in the original column:
            this_record_xid = [ fp[0]       # Export_data returns a vector, not a dictionary...
                for fp in all_field_pairs
                if fp[1]==raw_data ]        # Ditto
            if len(this_record_xid) == 0:
                data[lini][coli] = ""
            elif len(this_record_xid) > 1:
                print("Foi encontrado mais de um registo com a coluna %s='%s' usada como chave . . ." %
                        (key_field, raw_data))
                exit(-1)
            else:
                data[lini][coli] = this_record_xid[0]
        header[coli] = "id"
        

    def cook_csv_byfield(self, themodel, header, data, coli, context={}):
        # Proccess byfield headers:
        header_splited = header[coli].split(' byfield ')
        # Replace byfield headers by db id calls:
        header[coli] = header_splited[0]+"/id"
        # Find out what model that column points to:
        relat_column_model = self.find_relation_model(themodel, header_splited[0])
        # Get all values present in that column:
        all_field_values = list(set([ lin[coli] for lin in data ]))
        # Get External IDs of all records corresponding to that entries:
        col_model_proxy = self.odoo_connection.get_model(relat_column_model)
        field_correspondence_context = {**context, **self.connection_context, **{'active_test': False}, }
        all_field_ids = col_model_proxy.search(
                [(header_splited[1], 'in', all_field_values)],
                context=field_correspondence_context, )
        all_field_pairs = col_model_proxy.export_data(
                all_field_ids,
                ['id', header_splited[1]],
                context=field_correspondence_context )['datas']
        # On by one, find the id on the list that was returned by the server, and replace:
        for lini in range(len(data)):
            raw_data = data[lini][coli]
            if raw_data.strip()=='':
                data[lini][coli] = False
            else:
                this_record_db_id = [ fp[0]
                    for fp in all_field_pairs
                    if fp[1]==raw_data ]
                if len(this_record_db_id) == 0:
                    print("Não foi encontrado nenhum registo com a %s='%s' no modelo %s . . ." %
                            (header_splited[1], raw_data, relat_column_model))
                    exit(-1)
                elif len(this_record_db_id) > 1:
                    print("Foi encontrado mais de um registo com a coluna %s='%s' no modelo %s . . ." %
                            (header_splited[1], raw_data, relat_column_model))
                    exit(-1)
                data[lini][coli] = this_record_db_id[0]

    def cook_csv(self, themodel, header, data, context={}):
        for coli in range(len(header)):
            if   " byfield " in header[coli]:
                self.cook_csv_byfield(themodel, header, data, coli, context=context)
            elif re.search("^askey:.*$", header[coli], flags=0):
                self.cook_csv_askey(themodel, header, data, coli, context=context)
        #if themodel=='product.template': pdb.set_trace()

    def load_csv(self, conn_parms, infilenm, modelname, context={}):
        def load_csv_can_fail(self, conn_parms, infilenm, modelname, context={}):
            # Build config file programmatically:
            config_file = tempfile.TemporaryFile()
            config_file_data = bytes("""
    [Connection]
    hostname=%(hostname)s
    database=%(database)s
    login=%(login)s
    password=%(password)s
    protocol=%(protocol)s
    port=%(port)s
    uid=%(user_id)d
    """ % conn_parms, "utf-8")
            #print("Config file data is: "+str(config_file_data, "utf-8"))
            config_file.write(config_file_data)
            config_file.flush()
            config_file.seek(0)
            # Read file in, so that we can cook on it:
            fail_filename = infilenm+".fail"
            os.close(os.open(fail_filename, os.O_CREAT))
            encoding='utf-8'
            separator = ';'
            header, data = csv_read_file(infilenm, delimiter=separator, encoding=encoding)
            # Cook the CSV as we want it:
            self.cook_csv(modelname, header, data, context=context)
            check_id_column(header)
            #print(repr([ header, data ]))
            # Call lib function:
            ret = import_threaded.import_data(
                [config_file.name],
                modelname,
                #file_csv=infilenm,
                header=header,
                data=data,
                # One time I added {'active_test': False} to the context, but it is
                # useless here and it causes problems when loading groups (maybe
                # because the proccess of adding users to groups needs to modify
                # views)...
                context={ **context, **self.connection_context, },
                fail_file=fail_filename,
                encoding=encoding,
                separator=separator)
            # Close and delete the temp file:
            #tmpfile.close()
            ####################################################
            #import_data(   config_file, model, header=None, data=None, file_csv=None, context=None, fail_file=False, encoding='utf-8', separator=';',
            #               ignore=False, split=False, check=True, max_connection=1, batch_size=10, skip=0, o2m=False)
            #               header and data mandatory in file_csv is not provided
            #import_threaded.import_data(
            #        args.config, args.model, file_csv=file_csv, context=context,
            #        fail_file=fail_file, encoding=encoding, separator=args.separator,
            #        ignore=ignore, split=args.split, check=args.check,
            #        max_connection=max_connection, batch_size=batch_size, skip=int(args.skip), o2m=args.o2m)
            with open(fail_filename, "r") as ff:
                allerrors = ff.read().strip()
                if allerrors.find("\n") != -1:
                    raise OdooCommException("!!! Data file load error. the following records were not loaded:\n" + allerrors)
            return ret
        
        import_retry = [ True, 0 ]
        while import_retry[0]:
            try:
                ret = load_csv_can_fail(self, conn_parms, infilenm, modelname, context=context)
                print("[ OK ] Importação completa.")
                import_retry[0] = False
            except Exception as ex:
                import_retry[1] += 1
                if import_retry[1] < 5:
                    print("!!!!!! Tentar novamente...")
                    import_retry[0] = True
                else:
                    import_retry[0] = False
                    print("!!!!!! Importação falhou após 5 tentativas. Excepção:")
                    raise ex
        self.reconnect()
        return ret

    def direct_load_csv(self, infilenm, modelname, context={}):
        # Read file in, so that we can cook on it:
        encoding='utf-8'
        separator = ';'
        header, data = csv_read_file(infilenm, delimiter=separator, encoding=encoding)
        # Prune empty lines:
        data = [ dr for dr in data if any(dr) ]
        # Cook the CSV as we want it:
        self.cook_csv(modelname, header, data, context=context)
        check_id_column(header)
        # Call Odoo server:
        ret = self.doload(modelname, header, data, context)
        # Call lib function:
        return ret

    # CSV Load:
    def import_csv(self, modelname, context={}, locdir=".", filename=False):
        # Calculate names:
        if not filename:
            filename = modelname+".csv"
        filepath = os.path.join(locdir, filename)
        # Do the data load:
        ret = self.direct_load_csv(infilenm=filepath, modelname=modelname, context=context)
        #ret = self.load_csv(conn_parms=self.connection_params, infilenm=filepath, modelname=modelname, context=context)
        #print("========================")
        #print("========================")
        #print("========================")
        #print("== O Erro: %s"%str(ret))
        #print("========================")
        #print("========================")
        #print("========================")
        return ret
    
    ############################################################
    ### Translations: ##########################################
    ############################################################
    def delete_module_translations(self, lang, modname, omit_restrictive_models=True):
        print("A apagar traduções do módulo '%s'..."%modname)
        translations_model = self.sudo().get_model("ir.translation")
        #translations_model = self.odoo_connection.get_model("ir.translation")
        dom = [
            ('module', '=', modname),
            #*([
            #    # Odoo forbids deleting translations for the following models, so keep them instead:
            #    "!", ('name', '=like', 'ir.module.category,%'),
            #    "!", ('name', '=like', 'ir.actions.client,%'),
            #    "!", ('name', '=like', 'date.range.type,%'),
            #    "!", ('name', '=like', 'account.account.tag,%'),
            #    ] if omit_restrictive_models else [])
            ]
        if lang is not None:
            dom.append( ('lang', '=', lang) )
        to_del_ids = translations_model.search(dom)
        translations_model.unlink(to_del_ids)
    def load_translation(self, isocode):
        add_language_wizard_model = self.odoo_connection.get_model("base.language.install")
        wizard_instance = add_language_wizard_model.create({
                    'lang'        : isocode,
                    'overwrite'   : True,
                    })
        add_language_wizard_model.lang_install(wizard_instance)
    
    def import_translation_file(self, isocode, filename):
        print("A carregar ficheiro de traduções %s para %s." % (filename, isocode))
        # Load the CSV translation as binary data:
        with open(filename, "rb") as trans_file:
            trans_data = base64.encodebytes(trans_file.read())
        # Load it onto the database:
        import_language_wizard_model = self.odoo_connection.get_model("base.language.import")
        wizard_instance = import_language_wizard_model.create({
                    'name'          : isocode,
                    'code'          : isocode,
                    'filename'      : filename,
                    'data'          : str(trans_data, "iso-8859-15"),
                    'overwrite'     : True,
                    })
        import_language_wizard_model.import_lang(wizard_instance)
    
    def export_translation_file(self, isocode, appname, filename):
        print("A exportar tradução %s para o ficheiro %s..." % (isocode, filename))
        # Export it from the database:
        export_language_wizard_model = self.odoo_connection.get_model("base.language.export")
        wizard_instance = export_language_wizard_model.create({
                    'lang'          : isocode,
                    'format'        : 'po',
                    'modules/name'  : appname,
                    #'filename'      : filename,
                    #'data'          : str(trans_data, "iso-8859-15"),
                    #'overwrite'     : True,
                    })
        export_language_wizard_model.act_getfile(wizard_instance)
    
    # Correção de traduções por find&replace:
    def patch_translation(self, lang, to_find, replace_to):
        print("# Corrigir tradução '%s': subst '%s' por '%s'..."%(lang, to_find, replace_to))
        TRANSLATION_DUMP_HEADER = ['id', 'value']
        # Encontrar registos com ocorrências:
        translations_model = self.odoo_connection.get_model("ir.translation")
        #to_fix = translations_model.search_read([
        #                ('lang',    '=',        lang),
        #                ('value',   'like',   to_find),   ])
        to_fix_ids = translations_model.search([
                        ('lang',    '=',        lang),
                        ('value',   'like',   to_find),   ])
        to_fix = translations_model.export_data(to_fix_ids, TRANSLATION_DUMP_HEADER)
        # Traduzir as entrdas recebidas:
        print("Traduzir entradas", end=": ")
        n_translated = 0
        for trans in to_fix['datas']:
            n_translated += 1
            print(str(n_translated), end="... ")
            trans[1] = re.sub(to_find, replace_to, trans[1])
        print()
        #print(str(to_fix['datas']))
        # Enviar de volta para a base de dados:
        print("Enviar de volta à base de dados", end="...")
        translations_model.load(TRANSLATION_DUMP_HEADER, to_fix['datas'])
        print()
    
    # Correção de traduções por find&replace:
    def delete_translation(self, lang, to_find, modules=False):
        translations_model = self.odoo_connection.get_model("ir.translation")
        # Find them:
        domain = [
            ('lang',    '=',        lang),
            ('value',   'like',     to_find),   ]
        if modules:
            domain.append(('module', 'in', modules))
        to_del_ids = translations_model.search(domain)
        # Delete them:
        print("# A apagar traduções para '%s': %d ocorrências"%(lang, len(to_del_ids)))
        to_fix = translations_model.unlink(to_del_ids)
        print()
    
    def warn_word(self, lang, to_find):
        TRANSLATION_DUMP_HEADER = ['id', 'module', 'value']
        # Encontrar registos com ocorrências:
        translations_model = self.odoo_connection.get_model("ir.translation")
        #to_fix = translations_model.search_read([
        #                ('lang',    '=',        lang),
        #                ('value',   'like',   to_find),   ])
        to_fix_ids = translations_model.search([
                        ('lang',    '=',        lang),
                        ('value',   'like',   to_find),   ])
        if len(to_fix_ids) == 0:
            return False
        # Dump the translation and warn user:
        to_fix = translations_model.export_data(to_fix_ids, TRANSLATION_DUMP_HEADER)
        # Traduzir as entrdas recebidas:
        print("== Falta traduzir as seguintes entradas", end=": ")
        n_translated = 0
        for trans in to_fix['datas']:
            n_translated += 1
            print(str(n_translated)+". "+str(trans))
        exit(-1)
        return True
    
    ############################################################################
    ### Special Data Loads - Employees: ########################################
    ############################################################################
    def load_ods(self, doc, sheet_id, headers=True, columns=None):
        from collections import OrderedDict
        "This function was 'stolen' from pandas_ods_reader source code. License is 'MIT'."
        # convert the sheet to a pandas.DataFrame
        if not isinstance(sheet_id, (int, str)):
            raise ValueError("Sheet id has to be either `str` or `int`")
        if isinstance(sheet_id, str):
            sheets = [sheet.name for sheet in doc.sheets]
            if sheet_id not in sheets:
                raise KeyError("There is no sheet named {}".format(sheet_id))
            sheet_id = sheets.index(sheet_id) + 1
        sheet = doc.sheets[sheet_id - 1]
        df_dict = OrderedDict()
        col_index = {}
        for i, row in enumerate(sheet.rows()):
            # row is a list of cells
            if headers and i == 0 and not columns:
                # columns as lists in a dictionary
                columns = []
                for cell in row:
                    if cell.value and cell.value not in columns:
                        columns.append(cell.value)
                    else:
                        column_name = cell.value if cell.value else "unnamed"
                        # add count to column name
                        idx = 1
                        while "{}.{}".format(column_name, idx) in columns:
                            idx += 1
                        columns.append("{}.{}".format(column_name, idx))

                df_dict = OrderedDict((column, []) for column in columns)
                # create index for the column headers
                col_index = {
                    j: column for j, column in enumerate(columns)
                }
                continue
            elif i == 0:
                columns = columns if columns else (
                    [f"column.{j}" for j in range(len(row))])
                # columns as lists in a dictionary
                df_dict = OrderedDict((column, []) for column in columns)
                # create index for the column headers
                col_index = {j: column for j, column in enumerate(columns)}
                if headers:
                    continue
            for j, cell in enumerate(row):
                if j < len(col_index):
                    # Properly convert cell data:
                    if cell.value_type in ('string', None):
                        the_data = cell.value
                    elif cell.value_type in ('float',):
                        if int(cell.value)==cell.value:
                            the_data = str(int(cell.value))
                        else:
                            the_data = str(cell.value)
                    else:
                        print("TODO: cell.value_type = "+str(cell.value_type))
                        exit(-1)
                    # use header instead of column index
                    df_dict[col_index[j]].append(the_data)
                else:
                    continue
        return df_dict

    LINK_WORDS = ('de', 'do', 'da', 'dos', 'das', 'e', )

    def fix_employee_name(self, orinm):
        "Recapitalizes employee name."
        name_fragments = orinm.lower().split()
        def fix_one_word(nmword):
            if nmword in self.LINK_WORDS:
                return nmword.lower()
            else:
                return nmword.capitalize()
        fixed_words = map(fix_one_word, name_fragments)
        return " ".join(fixed_words)

    # Remove acentos, espaço duplicados e outros acidentes, e converte o nome para uma mistura de
    # palavras e iniciais separadas por underscores:
    def unify_employee_name(self, namee):
        namee = self.fix_employee_name(namee)
        #pdb.set_trace()
        namesake = remove_accents(re.sub("[\t\n ./\\']+", " ", namee).lower().strip())  # Remover acidentes, minuscular tudo
        namesake_fragments = namesake.split()                                           # Separar por fragmentos;
        namesake_fragments = tuple(filter(lambda s:
                        s.lower() not in self.LINK_WORDS, namesake_fragments))               # Remover palavras de ligação;
        #initials = "".join(map(lambda snm: snm[0], namesake[1:]))                      # (não) Sacar inciais (pode ser útil em alguns casos)
        return "".join(namesake_fragments)

    def fix_nif(self, orinif):
        nif = orinif.replace(' ', '')
        if not nif.startswith('PT'):
            nif = 'PT'+nif
        # Throw error if any char is not number:
        if not (nif[2:]).isdigit():
            print("NIF inválido: %s"%orinif)
        return nif

    def load_employees_informed(self, filepath, xid_module, load_receivable_accounts=False):
        # TODO: This has some problems, namely typing problems of column names. Needs to be rewritten:
        colnames = ('id_name_base', 'nif', 'name', 'related_partner_xid', 'payable_account_code',)
        if load_receivable_accounts:
            colnames = colnames + ('receivable_account_code',)
        # Model proxy objects:
        EmployeeModel = self.odoo_connection.get_model("hr.employee")
        PartnerModel = self.odoo_connection.get_model("res.partner")
        # Import from the ODS:
        thedoc = ezodf.opendoc(filepath)
        src_ods = self.load_ods(thedoc, 1)
        # Convert the ODS dictionary to a format suitable for the load() method.
        loadable_partners_cols = ['id', 'name', 'vat', 'employee', 'property_account_payable_id']
        loadable_partners = []
        loadable_employees_cols = ['id', 'name', 'address_home_id/id']
        loadable_employees = []
        # If load load_receivable_accounts....
        if load_receivable_accounts:
            loadable_partners_cols.append('property_account_receivable_id')
        # Read out all parters to find if there is need to create new partners:
        all_partners = PartnerModel.search_read([], fields=loadable_partners_cols)
        all_partners = list(map(lambda part: {'id': part['id'], 'name': part['name'], 'vat': part['vat'],
                    'unified_name': self.unify_employee_name(part['name']),
                    'unified_vat': self.fix_nif(part['vat']) if part['vat'] else "",
                    }, all_partners))
        for i in range(len(tuple(src_ods.values())[0])):
            # Raw Cols:
            rawcols = {}
            for colname in colnames:
                rawcols[colname] = src_ods[colname][i]
            if not rawcols['id_name_base']:
                continue
            print("A importar Funcionário: "+repr(rawcols))
            # Cols:
            col_id_name_base = rawcols['id_name_base']
            col_nif = self.fix_nif(rawcols['nif']) if rawcols['nif'] else False
            col_name = self.fix_employee_name(rawcols['name'])
            col_related_partner_xid = rawcols['related_partner_xid']
            col_payable_account_code = rawcols['payable_account_code']
            # Unified versions of cols:
            unified_name = self.unify_employee_name(rawcols['name'])
            ### Build the load list for partners:
            # Find a partner with that NIF, and of there is none, find one with the same name:
            if not col_related_partner_xid:
                # Fallback if partner does not exist or exists but has no xid:
                col_related_partner_xid = xid_module+".emppartner_"+col_id_name_base
                # Find a similar existing partner:
                existing_partner = list(filter(lambda emp: col_nif and emp['unified_vat']==col_nif, all_partners))
                if len(existing_partner)==0:
                    existing_partner = list(filter(lambda emp: emp['unified_name']==unified_name, all_partners))
                # Only create partner if there is none:
                if len(existing_partner)>0:
                    existing_partner_id = existing_partner[0]['id']
                    existing_partner_dxid = self.get_xid('res.partner', existing_partner_id)
                    if existing_partner_dxid:
                        col_related_partner_xid = existing_partner_dxid['module']+'.'+existing_partner_dxid['name']
                    else:
                        self.assign_xid(col_related_partner_xid.split('.')[0], col_related_partner_xid.split('.')[1], 'res.partner', existing_partner_id)
            loadlist = [
                col_related_partner_xid,
                self.fix_employee_name(col_name),
                col_nif,
                "True",
                col_payable_account_code,
                ]
            if load_receivable_accounts:
                loadlist.append(rawcols['receivable_account_code'])
            loadable_partners.append(loadlist)
            # Build the load list for employees:
            loadable_employees.append([
                xid_module+".emp_"+col_id_name_base,
                self.fix_employee_name(col_name),
                col_related_partner_xid,
                ])
        # First load partners, then employees, finally ibans (they may already
        # exist overwritten by the load() method):
        self.doload("res.partner", loadable_partners_cols, loadable_partners, context={})
        self.doload("hr.employee", loadable_employees_cols, loadable_employees, context={})
