# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Prisme postit',
    'version': '2017-03-08 16:17',
    'category': 'Tools',
    'summary': "task manager, reminder",
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'summary': 'tasks and reminders manager',
    'sequence': 9,
    'depends': [
        'mail',
    ],
    'data': [
        'postit_view.xml',
        'postit_workflow.xml',

    ],
    'demo': [

    ],
    'test': [
    ],
    'init_xml': [
    'init_scheduler.xml',

    ],
    'update_xml': [
    'security/ir.model.access.csv',
    ],
    'css': [
      #  'static/src/css/note.css',
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
