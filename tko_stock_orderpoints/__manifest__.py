# -*- encoding: utf-8 -*-

{
    'name': 'tko_stock',
    'version': '0.01',
    'category': 'Customizations',
    'sequence': 38,
    'complexity': 'medium',
    'description': ''' This module allows configure orderpoints subtracting quantity on hand of product
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'depends': [
        'stock',
    ],
    'data': [
        'stock_view.xml',
    ],
    'init': [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
