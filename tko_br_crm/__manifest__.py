# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Legal Names and CNPJ_CPF fields',
    'summary': '',
    'description': 'View of the Legal Name and CNPJ_CPF fields.',
    'author': 'TKO',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'br_base',
                'crm',
                'tko_base_partner_poc',
                'tko_crm_poc',
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
             'views/crm_opportunity_view.xml',
    ],
}
