# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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
    'name': 'Account Contract Report Template',
    'version': '0.055',
    'category': 'Account',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''Account Contract Report.''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg',],
    'depends': [
                'base',
                'analytic',
                'account_analytic_analysis',#contract
                'hr_timesheet_invoice', # to place button <header> tag is created in this module
                ],
    'init_xml': [],
    'data': [
             'data/contract_data_view.xml',
             'security/ir.model.access.csv',
             'report/contract_report_view.xml',
             'report/contract_report_template_view.xml',
             'wizard/contract_template_wizard_view.xml',
             'contract_mail_template.xml',
             'account_analytic_contract_view.xml',
             
             ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
