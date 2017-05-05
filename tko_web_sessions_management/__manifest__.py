# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web Sessions Management',
    'summary': '',
    'description': 'Sessions timeout and forced termination. Multisession control. Login by calendar (week day hours). Remote IP filter and location.',
    'author': 'TKO',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': [
                'base',
                'resource',
                'web',
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
             'security/ir.model.access.csv',
             'views/scheduler.xml',
             'views/res_users_view.xml',
             'views/res_groups_view.xml',
             'views/ir_sessions_view.xml',
             'views/webclient_templates.xml',
    ],
}
