# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Tko Purchase Request',
    'summary': '',
    'description': 'This module add domain in purchase line for analytic accounts',
    'author': 'TKO',
    'category': 'Purchases',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': ['purchase',
                'tko_account_analytic_type',
                ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'test': [],
    'data': [
        'views/tko_purchase_view.xml',
             ],

}
