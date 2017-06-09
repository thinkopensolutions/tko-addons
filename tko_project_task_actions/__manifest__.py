# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Task Actions',
    'summary': '',
    'description': 'Adds actions in task. Actions have rules and can execute server actions when concluded or cancelled (eg: add another action or create a task).',
    'author': 'TKO',
    'category': 'Project',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'base',
                'project',
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
        'views/project_task_view.xml',
        'wizard/cancel_conclude_view.xml',
        'data/cron_view.xml',
    ],
}
