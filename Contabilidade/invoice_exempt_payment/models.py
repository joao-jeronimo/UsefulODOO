# -*- coding: utf-8 -*-
#import babel
#from datetime import date, datetime, time
#from dateutil.relativedelta import relativedelta
#from pytz import timezone
#from odoo.tools.safe_eval import safe_eval
from odoo import api, fields, models, tools, _
from odoo.http import request
#from odoo.addons import decimal_precision as dp
#from odoo.exceptions import UserError, ValidationError
#from odoo.addons.helper_mod import util as helper_util

#import logging
#_logger = logging.getLogger(__name__)
#import sys, traceback
import pdb

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    payment_type = fields.Selection(selection_add = [
            ('outbound_invoice_exempt', 'Send Money (no invoice)'),
            ('inbound_invoice_exempt', 'Receive Money (no invoice)'),
            ])
    
    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for payment in self:
            if payment.payment_type in ('outbound_invoice_exempt', 'outbound_invoice_exempt'):
                
