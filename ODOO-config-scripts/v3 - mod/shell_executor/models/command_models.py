# -*- coding: utf-8 -*-
#import babel
#from datetime import date, datetime, time
#from dateutil.relativedelta import relativedelta
#from pytz import timezone
#from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, tools, _
#from odoo.addons import decimal_precision as dp
#from odoo.exceptions import UserError, ValidationError
#from odoo.addons.<modulename>.util import *

#import logging
#_logger = logging.getLogger(__name__)

#import sys, traceback
#import pudb


class MyExperienceModuçe(models.Model):
    _name = 'access_server.command'
    
    name = fields.Char(string="Name")
