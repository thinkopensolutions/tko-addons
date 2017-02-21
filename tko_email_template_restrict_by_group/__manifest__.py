# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Thinkopen - Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com.br>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Restrict Mail Templates by User Groups',
    'category': 'Mail',
    'author': 'ThinkOpen Solutions Brasil, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://tkobr.com',
    'description': ''' This module applies restrictions on email tempatlates by using user groups''',
    'version': '10.0.2.0.0',
    'sequence': 10,
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/mail_compose_view.xml',
        'views/mail_template_view.xml',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    'auto_install': False,
    'certificate': '',
}
