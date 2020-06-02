# -*- coding: utf-8 -*-
#import babel
#from datetime import date, datetime, time
#from dateutil.relativedelta import relativedelta
#from pytz import timezone
#from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, tools, _
#from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
#from odoo.addons.<modulename>.util import *
import json

import requests

#import logging
#_logger = logging.getLogger(__name__)

#import sys, traceback
import pdb
#import pudb


class DirectionsServer(models.Model):
    _name = 'directions.server'
    
    name = fields.Char()
    url = fields.Char()
    api_key = fields.Char()
    
    def get_route(self, request):
        # Build request:
        url = self.url
        url += "/v2/directions/driving-car?"
        url_params= [
            ("api_key=%(api_key)s" % {'api_key': self.api_key}),
            ("start=%(start_lat)f,%(start_long)f" % {'start_lat': request.src_lat, 'start_long': request.src_long, }),
            ("end=%(end_lat)f,%(end_long)f" % {'end_lat': request.dst_lat, 'end_long': request.dst_long, }),
            ]
        url += "&".join(url_params)
        # Make the request:
        r = requests.get(url)
        if r.status_code!=200:
            #pdb.set_trace()
            err = _("HTTP error code %d.\nRequest URL was: %s") % (r.status_code, url)
            print(err)
            #raise UserError(err)
        # Interpret the JSON and build the direction:
        json_response = json.loads(r.text)
        #pdb.set_trace()
        waypoints_dikts = list(map(lambda wp: (0, -999, { 'waypoint_lat': wp[0], 'waypoint_long': wp[0], }),
                                   json_response['features'][0]['geometry']['coordinates']))
        return {
            'distance':         json_response['features'][0]['properties']['segments'][0]['distance'],
            'fullfils_id':      request.id,
            'server_id':        self.id,
            'waypoints_ids':    waypoints_dikts,
            }
