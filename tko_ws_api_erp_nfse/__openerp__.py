# -*- encoding: utf-8 -*-
##############################################################################
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is NOT free software.
#
##############################################################################

{
    'name': 'TKOBR WS API for São Paulo NFSe',
    'version': '0.002',
    'category': 'Customization',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== TKOBR WS API for São Paulo NFSe ==
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
              ],
    'depends': ['base',
                'account',
                'l10n_br_base',
               ],
    'data': [
             'views/account_invoice_view.xml',
             'workflow/account_invoice_workflow.xml',
             ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [], #YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False, #If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
