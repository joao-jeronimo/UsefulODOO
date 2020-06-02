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


class DirectionsRouteRequest(models.Model):
    _name = 'directions.route.request'
    
    #def name_get(selfs):
    #    res = []
    #    for self in selfs:
    #        repres = self.name
    #        res.append((self.id, repres))
    #    return res
    
    name = fields.Char ("Name", readonly=True, compute="_compute_name")
    def _compute_name(selfs):
        for self in selfs:
            self.name = (_("Route request from lat=%.9f;long=%.9f to lat=%.9f;long=%.9f")
                            % (self.src_lat, self.src_long, self.dst_lat, self.dst_long))
    
    date_requested = fields.Datetime("Time requested")
    date_fetched = fields.Datetime("Time fetched")
    
    src_lat = fields.Float("Source Latitude", digits=(13, 9))
    src_long = fields.Float("Source Longitude", digits=(13, 9))
    dst_lat = fields.Float("Destination Latitude", digits=(13, 9))
    dst_long = fields.Float("Destination Longitude", digits=(13, 9))
    
    def button_fetch(self):
        self.ensure_one()
        self.fetch_from_server(self.env['directions.server'].search([], limit=1))
    
    def fetch_from_server(self, server):
        
        
        
        self.date_fetched = fields.Datetime.now()
