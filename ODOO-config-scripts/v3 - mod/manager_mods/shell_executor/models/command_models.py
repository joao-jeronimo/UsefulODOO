# -*- coding: utf-8 -*-
#import babel
#from datetime import date, datetime, time
#from dateutil.relativedelta import relativedelta
#from pytz import timezone
from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, tools, _
#from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons.shell_executor.util import proclib
import subprocess

#import logging
#_logger = logging.getLogger(__name__)

import os, sys, traceback
#import pudb


class ExecutorCommand(models.Model):
    _name = 'access_server.command'
    
    name = fields.Char(string="Name")
    bash_code = fields.Text(string="Bash code to execute")
    
    def execute(self, outfilename, locals_dict={}):
        self.ensure_one()
        # Substitute arguments:
        real_bash_code = self.bash_code%locals_dict
        # Execute the code on local host:
        with open(outfilename, "w") as outfile:
            subprocess.Popen( ['/bin/bash', '-c', real_bash_code], stdout=outfile, stderr=subprocess.STDOUT)

class ExecutorCommandCall(models.Model):
    _name = 'access_server.command.call'
    
    state = fields.Selection([
                ('never_executed',  "Never Executed"),
                ('done',            "Done"),
                ('now_executing',   "Now Executing"),
                ], string="State", default='never_executed', compute="_compute_state")
    def _compute_state(calls):
        for self in calls:
            filename = self.get_stdout_filename()
            if not os.path.isfile(filename):
                self.state = 'never_executed'
            else:
                fuser_exitcode = subprocess.Popen( ['fuser', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
                if fuser_exitcode == 0:
                    self.state = 'now_executing'
                else:
                    self.state = 'done'
    
    base_command = fields.Many2one("access_server.command", string="The base command to execute")
    arguments_ids = fields.One2many("access_server.command.argument", inverse_name="call_id",
                                   string="Arguments")
    bash_result = fields.Text(string="Command result", compute="_compute_bash_result")
    def _compute_bash_result(self):
        for thisCall in self:
            filename = thisCall.get_stdout_filename()
            if os.path.isfile(filename):
                with open(filename, "r") as theFile:
                    thisCall.bash_result = theFile.read()
            else:
                thisCall.bash_result = "(Never executed)"
    
    def get_stdout_filename(self):
        return "/odoo/logs/manager/"+str(self.id)
    
    def name_get(self):
        res = []
        for c in self:
            repres = _("%s") % (self.base_command.name, )
            res.append((c.id, repres))
        return res
    
    #####################
    ### Buttons: ########
    #####################
    def button_execute(self, otherargs={}):
        self.ensure_one()
        # Cancel if already executing:
        if self.state=='now_executing':
            raise UserError("Already executing.")
        # Do execute:
        locals_dict = dict()
        for thisArg in self.arguments_ids:
            locals_dict[thisArg.key] = thisArg.value
        locals_dict.update(otherargs)
        self.base_command.execute(self.get_stdout_filename(), locals_dict)

class ExecutorCommandArgument(models.Model):
    _name = 'access_server.command.argument'
    
    call_id = fields.Many2one("access_server.command.call")
    key = fields.Char(string="Key")
    value = fields.Text(string="Value of the argument")
    
    def name_get(self):
        res = []
        for c in self:
            repres = _("(%s: %s)") % (c.key, c.value, )
            res.append((c.id, repres))
        return res
