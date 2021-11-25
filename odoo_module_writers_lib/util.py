##############################################################################
#
#    Author: João Jerónimo (joao.jeronimo.pro@gmail.com)
#    Copyright (C) 2019 - All rights reserved
#
##############################################################################

import math
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from datetime import datetime, date, timedelta
#import dateutil.relativedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
#import logging
#_logger = logging.getLogger(__name__)
#import pudb


###############################
### Non-date stuff: ###########
###############################
def constrain(x, a, b):
    if x<a:
        return a
    elif x>b:
        return b
    else:
        return x

def concat_lists(thelists):
    return sum(thelists, [])
