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
    'name': 'Localização Brasileira para Recursos Humanos',
    'version': '0.001',
    'category': 'l10n_br',
    'sequence': 9,
    'complexity': 'normal',
    'description': '''=== Localização Brasileira Recursos Humanos ===\n\n
Este módulo adiciona campos de cadastro gerais aos empregados.\n
Entre outros adiciona:\n
 - Documentos, RG, Passaporte, etc...\n
 - Habilitações\n
 - Exames médicos\n''',
    'author': 'ThinkOpen Solutions Brasil',
    'license': 'AGPL-3',
    'website': 'http://www.tkobr.com',
    'depends': [
                'base',
                'hr',
                ],
    'data': [
             'data/hr.religion.csv',
             'data/grau.instrucao.csv',
             'data/tipo.exame.csv',
             'data/hr.local.csv',
             'data/hr.parentesco.csv',
             'data/tipo.evento.csv',
             'data/hr.motivo.csv',
             'data/conselho.regional.csv',
             'data/orgao.expedidor.csv',
             'data/categoria.habilitacao.csv',
             'security/ir.model.access.csv',
             'l10n_br_hr_view.xml',
             'l10n_br_extra_views.xml',
             ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
