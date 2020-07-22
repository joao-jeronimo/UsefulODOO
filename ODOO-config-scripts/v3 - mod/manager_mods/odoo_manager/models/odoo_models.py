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
from odoo.addons.shell_executor.util import compat
from odoo.addons.odoo_manager.konst import *

#import logging
#_logger = logging.getLogger(__name__)

#import sys, traceback
#import pudb


class OdooBranch(models.Model):
    _name = 'access_server.odoo.branch'
    
    state = fields.Selection([
        ('new', 'New'),
        ('fetched', 'Fetched'),
        ])
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Name on git", required=True)
    
    local_path = fields.Char(string="Local Path", compute="_compute_local_path", store=True)
    @compat.one
    @api.depends("code")
    def _compute_local_path(self):
        if self.code:
            self.local_path = RELEASES_DIR+"/b"+(self.code or '')
        else:
            self.local_path = _("N/D")
    
    base_call_id = fields.Many2one("access_server.command.call", required=True,
                                   string="Call to fetch this branch")
