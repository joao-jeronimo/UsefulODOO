#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Human resources demo data',
    'category': 'Human Resources',
    'sequence': 906,
    'license': 'LGPL-1',
    'application': False,
    'installable': True,
    
    # Version-dependent information:
    #'version': '11.1.0',
    #'version': '12.1.0',
    #'version': '13.1.0',
    'data': [
        'hr_demo.xml',
        'hr_contract_demo.xml',
        'hr_payroll_demo.xml',
    ],
    'depends': [
        # For Odoo11 and Odoo12:
        #'hr_payroll',
        
        # For Odoo13:
        'hr_payroll_community',
        
        # Common dependencies:
        'hr',
        'hr_contract',
    ],
}
