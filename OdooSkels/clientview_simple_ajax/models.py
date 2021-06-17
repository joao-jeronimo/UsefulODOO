# João Jerónimo
from odoo import models, fields, api
from datetime import datetime,date

class RichPayroll(models.Model):
    _name = "rich.payroll"
    
    @api.model
    def heatbiit(self):
        return " baboseiras no dia "+str( datetime.now() )
