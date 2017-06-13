# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'tko_stock_inventory_adjustments',
    'version': '0.1',
    'category': 'Warehouse Management',
    'complexity': 'normal',
    'description': ''' Módulo de saída de estoque para funcionários da loja. ''',
    'author': 'TKO',
    'website': 'http://tko.tko-br.com',
    'depends': ['stock'],
    'data': [
        'views/stock_employee_inventory_form.xml.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
