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
    'name': 'Partner multiple phones and emails in a single tab',
    'version': '0.002',
    'category': 'Customizations',
    'sequence': 17,
    'complexity': 'normal',
    'description': '''== Partner Phones and Emails in a Single Tab Module ==\n\n
Merge into one single partner's tab the multiple phones and emails tabs.\n\n
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
              ],
    'depends': [
                'tko_partner_multiple_phones',
                'tko_partner_multiple_emails',
               ],
    'data': [
             'res_partner_view.xml',
             ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': True,  # If it's True, the module will be auto-installed when all dependencies are installed
    'certificate': '',
}
