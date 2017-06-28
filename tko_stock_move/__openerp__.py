# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'tko_stock_move',
    'version': '0.1',
    'category': 'Warehouse Management',
    'complexity': 'normal',
    'description': ''' 
                   Module to simplify daily stock transactions. 
                   ''',
    'author': 'TKO',
    'website': 'http://tko.tko-br.com',
    'depends': ['stock'],
    'data': ['stock_move_view.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,