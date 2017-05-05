# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'SMTP Server Per User',
    'summary': '',
    'description': 'Adds user in outgoing mail server.',
    'author': 'TKO',
    'category': 'Discuss',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.2.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'base',
                'mail',
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
             'security/ir.model.access.csv',
    ],
}
