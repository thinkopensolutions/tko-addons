# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Pagamento por Parcela',
    'summary': '',
    'description': 'Ao registrar um pagamento na fatura, permite escolher a parcela.',
    'author': 'TKO',
    'category': 'l10n_br',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': False,
    'auto_install': True,
    'depends': [
                'br_account',
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
             'wizard/account_voucher_view.xml',
             'account_invoice_view.xml',
    ],
}
