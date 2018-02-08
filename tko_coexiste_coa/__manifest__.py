# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Plano de Contas Brasileiro',
    'summary': '',
    'description': 'Plano de contas brasileiro adaptável a qualquer segmento.',
    'author': 'TKO',
    'category': 'l10n_br',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'account',
        'br_account',
        'account_parent',
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
        'data/chart_data.xml',
        'data/account.account.template.csv',
        'data/chart_data_properties.xml',
        # TODO Separate proprities for products vs. services (enhance data/chart_data_properties.xml)
        # TODO Criar Contas Pai
        # TODO Create & Import l10n_br Taxes
    ],
}
