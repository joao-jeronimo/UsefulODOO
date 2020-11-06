{
    'name':'Odoo Manager',
    'category': '',
    'version':'0.1',
    'author':'João Jerónimo',
    'data': [
        'views/odoo_views.xml',
        'views/menus.xml',
        'commands/prepare_odoo.xml',
    ],
    'depends': [
        'shell_executor',
        ],
    'auto_install': False,
    #'images': [
    #    'static/description/icon.png',
    #],
}
