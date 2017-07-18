# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Task Actions Assign',
    'summary': '',
    'description': 'Assign users to actions. In configuration set task_id.user_id or task_id.project_id.user_id to get dynamic assigned users.',
    'author': 'TKO',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,

    'auto_install': False,
    'depends': [
        'tko_project_task_actions_assign',
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
        'wizard/action_line_user_view.xml',
        'views/project_task_view.xml',
        'views/project_team_view.xml',
    ],
}
