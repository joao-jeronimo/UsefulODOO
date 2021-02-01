{
    'name': 'Create payments without involving payable or receivable accounts',
    'version':'0.1',
    'application': False,
    'data': [
        'views.xml',
        #'ir.model.access.csv',
    ],
    'depends': [
        'account',
    ],
    'auto_install': False,
    #'images': [
    #    'static/description/icon.png',
    #],
    
    #'pre_init_hook': 'pre_install_tasks',
    #'post_init_hook': 'post_install_tasks',
}
