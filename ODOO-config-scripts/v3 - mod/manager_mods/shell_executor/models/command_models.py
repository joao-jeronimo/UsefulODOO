# -*- coding: utf-8 -*-
#import babel
#from datetime import date, datetime, time
#from dateutil.relativedelta import relativedelta
#from pytz import timezone
from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, tools, _
#from odoo.addons import decimal_precision as dp
#from odoo.exceptions import UserError, ValidationError
from odoo.addons.shell_executor.util import proclib

#import logging
#_logger = logging.getLogger(__name__)

#import sys, traceback
#import pudb


class ExecutorCommand(models.Model):
    _name = 'access_server.command'
    
    name = fields.Char(string="Name")
    
    bash_code = fields.Text(string="Bash code to execute")
    def execute(self, locals_dict):
        self.ensure_one()
        # Substitute arguments:
        real_bash_code = self.bash_code%locals_dict
        # Execute the code on local host:
        bash_result = proclib.run_into_string(['/bin/bash', '-c', real_bash_code])
        # Save the resulting text:
        return bash_result
    
    bash_result = fields.Text(string="Command result")
    
    #####################
    ### Buttons: ########
    #####################
    def button_execute(self):
        self.ensure_one()
        self.bash_result = self.execute()

class ExecutorCommandCall(models.Model):
    _name = 'access_server.command.call'
    
    base_command = fields.Many2one("access_server.command", string="The base command to execute")
    arguments_ids = fields.One2many("access_server.command.argument", inverse_name="call_id",
                                   string="Arguments")
    bash_result = fields.Text(string="Command result")
    
    def name_get(self):
        res = []
        for c in self:
            repres = _("%s") % (self.base_command, )
            res.append((c.id, repres))
        return res
    
    #####################
    ### Buttons: ########
    #####################
    def button_execute(self):
        self.ensure_one()
        locals_dict = dict()
        for thisArg in self.arguments_ids:
            locals_dict[thisArg.key] = thisArg.value
        self.bash_result = self.base_command.execute(locals_dict)

class ExecutorCommandArgument(models.Model):
    _name = 'access_server.command.argument'
    
    call_id = fields.Many2one("access_server.command.call")
    key = fields.Char(string="Key")
    value = fields.Text(string="Value of the argument")
    
    def name_get(self):
        res = []
        for c in self:
            repres = _("(%s: %s)") % (self.key, self.value, )
            res.append((c.id, repres))
        return res
