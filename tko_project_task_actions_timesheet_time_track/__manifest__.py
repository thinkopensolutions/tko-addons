# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Thinkopen - Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com.br>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Track Time on Actions',
    'category': 'Project',
    'author': 'TKO',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-uk.com',
    'version': '10.0.1.0.0',
    'sequence': 11,
    'depends': [
        'tko_project_task_actions_timesheet',
    ],
    'data': [
        'views/project_task_view.xml',
    ],
    'external_dependencies': {
        'python': [],
        'bin': []
    },
    'init': [],
    'demo': [],
    'update': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'certificate': '',
}
