# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Total Discount',
    'summary': '',
    'description': 'Allows to add total discount, fixed or percentage, in sale order.',
    'author': 'TKO',
    'category': 'Sales',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'sale',
                'account',
    ],
    'external_dependencies': {
                                'python': [],
                                'bin': [],
                                },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'data': [
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
    ],
}
