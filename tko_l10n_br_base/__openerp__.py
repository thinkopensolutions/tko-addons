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
    'name': 'Customização da Localização Brasileira',
    'version': '0.035',
    'category': 'Localisation',
    'sequence': 4,
    'complexity': 'normal',
    'description': '''== CUSTOMIZAÇÃO DA LOCALIZAÇÃO BRASILEIRA ==\n\n
Este módulo melhora a legibilidade da tela de parceiro.\n
Também adiciona novos campos específicos, de cadastro de empresa:\n
 - Informação de negócio;\n
 - Organização dos contatos.\n
 Os dados da empresa e parceiro ficam sincronizados.\n''',
    'author': 'ThinkOpen Solutions Brasil',
    'license': 'AGPL-3',
    'website': 'http://www.tkobr.com',
    'depends': [
                'base',
                'l10n_br_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/activity_branch.csv',
        'data/business_size.csv',
        'data/annual_income.csv',
        'data/economic_sector.csv',
        'data/business_nationality.csv',
        'data/district.csv',
        'res_partner_view.xml',
        'res_company_view.xml',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    'auto_install': False,
    'certificate': '',
}
