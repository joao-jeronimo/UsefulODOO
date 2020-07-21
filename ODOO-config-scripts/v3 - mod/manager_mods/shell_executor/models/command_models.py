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
    def execute(self, **kwargs):
        self.ensure_one()
        locals_dict = dict()
        for key, value in kwargs.items():
            locals_dict[key] = velue
        # Substitute arguments:
        real_bash_code = self.bash_code%locals_dict
        # Execute the code on local host:
        bash_result = proclib.run_into_string(['/bin/bash', '-c', real_bash_code])
        # Save the resulting text:
        self.bash_result = bash_result
    
    bash_result = fields.Text(string="Command result")
    
    #####################
    ### Buttons: ########
    #####################
    def button_execute(self):
        self.execute()
