##############################################################################
#
#    Author: João Jerónimo (joao.jeronimo.pro@gmail.com)
#    Copyright (C) 2021 - All rights reserved
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


def term_filters_on_fieldnames(term_or_operator, fieldnames):
    if not isinstance(term_or_operator, (list, tuple)):
        return False
    assert len(term_or_operator)==3
    # Test the field names:
    if term_or_operator[0] in fieldnames:
        return True
    else:
        return False

def term_filters_on_values(term_or_operator, values):
    if not isinstance(term_or_operator, (list, tuple)):
        return False
    assert len(term_or_operator)==3
    # Test the field values:
    if isinstance(term_or_operator[2], (list, tuple)):
        return any((item in values) for item in term_or_operator[2])
    else:
        return term_or_operator[2] in values
