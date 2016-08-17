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

import time
from datetime import datetime, timedelta, date
from openerp.tools.translate import _
from openerp.osv import osv, fields
from openerp import tools


AVAILABLE_STATUS = [
    ('concluido', u'Concluído'),
    ('cursando', u'Cursando'),
    ('trancado', u'Trancado'),
]


AVAILABLE_LANGUAGE_STATUS = [
    ('concluido', u'Nativo'),
    ('cursando', u'Domínio'),
    ('trancado', u'Fluente'),
    ('trancado', u'Intermediário'),
    ('trancado', u'Básico'),
]


AVAILABLE_EXAM_STATUS = [
    ('apto', u'Apto'),
    ('inapto', u'Inapto'),
    ('apto_outra', u'Apto a Outra Funcção'),
    ('inapto_outra', u'Inapto a Outra Função'),
]


AVAILABLE_GENDER = [
    ('m', u'Masculino'),
    ('f', u'Feminino'),
]


class hr_religion(osv.Model):
    _name = 'hr.religion'
    _description = 'Religion'
    _order = 'name'

    _columns = {
        'name': fields.char(
            'Religion',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('hr_religion_unique', 'unique(name)', u'Religião já existe.'),
    ]


class hr_employee(osv.Model):
    _inherit = 'hr.employee'

    def _get_transportation_cost(
            self,
            cr,
            uid,
            ids,
            field_name,
            args,
            context=None):
        res = {}
        tranportation_cost = 0.0
        for emp in self.browse(cr, uid, ids, context=context):
            for cost in emp.cartao_transp_ids:
                tranportation_cost = tranportation_cost + cost.valor_cartao_transp
            res[emp.id] = tranportation_cost
        return res

    _columns = {
        'endereco_lotacao': fields.many2one('res.partner', u'Endereço de Lotação'),
        'mariage_date': fields.date('Marriage Date'),
        'is_handicapped': fields.boolean('Is Handicapped?'),
        'handicap_description': fields.text('Handicap Description'),
        'religion_id': fields.many2one('hr.religion', 'Religion'),
        'ctps': fields.char(u'CTPS Nº', size=32),
        'ctps_serie': fields.char(u'Série', size=32),
        'pis_pasep': fields.char(u'PIS/Pasep', size=32),
        'livro': fields.char('Livro', size=32),
        'folha': fields.char('Folha', size=32),
        'caixa': fields.char('Caixa', size=32),
        'cpf': fields.char('CPF', size=32),
        'cpf_orgao_expedidor_id': fields.many2one('orgao.expedidor', u'Órgão Expedidor'),
        'eleitor': fields.char(u'Título Eleitor', size=32),
        'habilitacao': fields.char(u'Habilitação', size=32),
        'habilitacao_categoria_id': fields.many2one('categoria.habilitacao', 'Categoria'),
        'habilitacao_validade': fields.date('Validade'),
        'oab_estado_id': fields.many2one('res.country.state', 'Estado Federal'),
        'oab_numero': fields.char('OAB', size=32),
        'oab_validade': fields.date('Validade'),
        'passaporte_orgao_expedidor_id': fields.many2one('orgao.expedidor', u'Órgão Expedidor'),
        'passaporte_validade': fields.date('Validade'),
        'rg': fields.char('RG', size=32),
        'rg_digito': fields.char('Dg', size=1),
        'rg_orgao_expedidor_id': fields.many2one('orgao.expedidor', u'Órgão Expedidor'),
        'rge': fields.char('RGE', size=32),
        'rge_digito': fields.char('Dg', size=1),
        'rge_orgao_expedidor_id': fields.many2one('orgao.expedidor', u'Órgão Expedidor'),
        'rg_militar': fields.char('RG Militar', size=32),
        'rg_militar_digito': fields.char('Dg', size=1),
        'rg_militar_orgao_expedidor_id': fields.many2one('orgao.expedidor', u'Órgão Expedidor'),
        'conselho_regional_id': fields.many2one('conselho.regional', 'Conselho Regional'),
        'conselho_regional_estado_id': fields.many2one('res.country.state', 'Estado Federal'),
        'conselho_regional_numero': fields.char(u'CR Nº', size=32),
        'conselho_regional_validade': fields.date('Validade'),
        'escolaridade_ids': fields.one2many('employee.escolaridade', 'employee_id'),
        'cursos_certificacoes_ids': fields.one2many('employee.cursos.certificacoes', 'employee_id'),
        'exame_medico_ids': fields.one2many('employee.exame.medico', 'employee_id'),
        'dependentes_ids': fields.one2many('employee.dependente', 'employee_id'),
        'idiomas_ids': fields.one2many('employee.idioma', 'employee_id'),
        'father_name': fields.char(u"Father's Name", size=256),
        'mother_name': fields.char(u"Mother's Name", size=256),
        'spec': fields.char("SPEC", size=64),
        'health_insurance': fields.boolean('Health Insurance'),
        'transportation_cost': fields.function(_get_transportation_cost, type='float', string=u'Condução'),
        'cartao_transp_ids': fields.one2many('hr.employee.transportation.card', 'employee_id', u'Cartão Transporte'),
        'meal_voucher': fields.float('Meal Voucher'),
        'health_insurance_value': fields.float('Health Insurance Value'),
    }


class hr_motivo(osv.Model):
    _name = 'hr.motivo'
    _description = u'Motivo'

    _columns = {
        'name': fields.char('Motivo', size=128, required=True, translate=True),
    }

    _sql_constraints = [
        ('hr_motivo_unique', 'unique(name)', u'Motivo já existe.'),
    ]


class employee_escolaridade(osv.Model):
    _name = 'employee.escolaridade'
    _description = 'Escolaridade'
    _order = 'date_start desc'

    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True),
        'grau_instrucao': fields.many2one(
            'grau.instrucao',
            u'Grau de Instrução',
            required=True),
        'instituicao': fields.many2one(
            'hr.instituicao',
            u'Instituição',
            required=True),
        'curso': fields.char(
            'Curso',
            size=128,
            required=True),
        'status': fields.selection(
            AVAILABLE_STATUS,
            'Status',
            required=True,
            translate=True),
        'date_start': fields.date(
            u'Data Início',
            required=True),
        'date_end': fields.date(u'Data Conclusão'),
        'observations': fields.text(u'Observações'),
    }

    _sql_constraints = [
        ('date_sequence',
         'CHECK ((date_end IS NOT NULL AND date_start <= date_end) OR date_end IS NULL)',
         u'A data de início deve ser menor que a data de finalização !'),
    ]


class employee_cursos_certificacoes(osv.Model):
    _name = 'employee.cursos.certificacoes'
    _description = u'Cursos e Certificações'
    _order = 'date_start desc'

    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True),
        'tipo_evento': fields.many2one(
            'tipo.evento',
            'Tipo Evento',
            required=True),
        'instituicao': fields.many2one(
            'hr.instituicao',
            u'Instituição',
            required=True),
        'curso': fields.char(
            'Curso',
            size=128,
            required=True),
        'status': fields.selection(
            AVAILABLE_STATUS,
            'Status',
            required=True,
            translate=True),
        'date_start': fields.date(
            u'Data Início',
            required=True),
        'date_end': fields.date(u'Data Conclusão'),
        'observations': fields.text(u'Observações'),
    }

    _sql_constraints = [
        ('date_sequence',
         'CHECK ((date_end IS NOT NULL AND date_start <= date_end) OR date_end IS NULL)',
         u'A data de início deve ser menor que a data de finalização !'),
    ]


class grau_instrucao(osv.Model):
    _name = 'grau.instrucao'
    _description = u'Grau de Instrução'

    _columns = {
        'name': fields.char('Grau', size=128, required=True, translate=True),
    }

    _sql_constraints = [
        ('grau_instrucao_unique',
         'unique(name)',
         u'Grau instrução já existe.'),
    ]


class tipo_evento(osv.Model):
    _name = 'tipo.evento'
    _description = 'Tipo Evento'

    _columns = {
        'name': fields.char(
            'Tipo Evento',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('tipo_evento_unique', 'unique(name)', u'Tipo evento já existe.'),
    ]


class hr_instituicao(osv.Model):
    _name = 'hr.instituicao'
    _description = u'Instituição'

    _columns = {
        'name': fields.char(
            u'Instituição',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('hr_instituicao_unique', 'unique(name)', u'Instituição já existe.'),
    ]


class employee_idioma(osv.Model):
    _name = 'employee.idioma'
    _description = 'Idiomas'
    _order = 'date_start desc'

    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True),
        'idioma': fields.selection(
            tools.scan_languages(),
            'Idioma',
            required=True),
        'instituicao': fields.many2one(
            'hr.instituicao',
            u'Instituição',
            required=True),
        'curso': fields.char(
            'Curso',
            size=128,
            required=True),
        'status': fields.selection(
            AVAILABLE_LANGUAGE_STATUS,
            'Status',
            required=True,
            translate=True),
        'date_start': fields.date(
            u'Data Início',
            required=True),
        'date_end': fields.date(u'Data Conclusão'),
        'observations': fields.text(u'Observações'),
    }

    _sql_constraints = [
        ('date_sequence',
         'CHECK ((date_end IS NOT NULL AND date_start <= date_end) OR date_end IS NULL)',
         u'A data de início deve ser menor que a data de finalização !'),
    ]


class employee_exame_medico(osv.Model):
    _name = 'employee.exame.medico'
    _description = u'Exame Médico'
    _order = 'data desc'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'tipo_exame': fields.many2one('tipo.exame', 'Tipo Exame', required=True),
        'data': fields.date('Data Início', required=True),
        'clinica': fields.many2one('hr.clinica', u'Clínica', required=True),
        'medico': fields.many2one('hr.medico', u'Médico', required=True),
        'local': fields.many2one('hr.local', 'Local', required=True),
        'os': fields.char('OS', size=16, required=True),
        'status': fields.selection(AVAILABLE_EXAM_STATUS, 'Status', required=True, translate=True),
    }


class tipo_exame(osv.Model):
    _name = 'tipo.exame'
    _description = 'Tipo Exame'

    _columns = {
        'name': fields.char(
            'Tipo Exame',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('tipo_exame_unique', 'unique(name)', u'Tipo exame já existe.'),
    ]


class hr_clinica(osv.Model):
    _name = 'hr.clinica'
    _description = u'Clínica'

    _columns = {
        'name': fields.char(
            u'Clínica',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('hr_clinica_unique', 'unique(name)', u'Clinica já existe.'),
    ]


class hr_medico(osv.Model):
    _name = 'hr.medico'
    _description = u'Médico'

    _columns = {
        'name': fields.char(
            u'Médico',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('hr_medico_unique', 'unique(name)', u'Médico já existe.'),
    ]


class hr_local(osv.Model):
    _name = 'hr.local'
    _description = 'Local'

    _columns = {
        'name': fields.char('Local', size=128, required=True, translate=True),
    }

    _sql_constraints = [
        ('hr_local_unique', 'unique(name)', u'Local já existe.'),
    ]


class employee_dependente(osv.Model):
    _name = 'employee.dependente'
    _description = 'Dependente'
    _order = 'birth_date desc'

    def _age(self, birth_date):
        now = date.today()
        age_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        age = now.year - age_date.year - (0 if (now.month > age_date.month or (
            now.month == age_date.month and now.day >= age_date.day)) else 1)
        return age

    def _calculate_age(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for partner in self.browse(cr, uid, ids):
            if partner.birth_date:
                res[partner.id] = self._age(partner.birth_date)
            else:
                res[partner.id] = 0
        return res

    _columns = {
        'name': fields.char(
            'Nome',
            size=256,
            required=True),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True),
        'sexo': fields.selection(
            AVAILABLE_GENDER,
            u'Género',
            required=True,
            translate=True),
        'birth_date': fields.date(
            'Data Nascimento',
            required=True),
        'parentesco': fields.many2one(
            'hr.parentesco',
            'Parentesco',
            required=True),
        'grau_instrucao': fields.many2one(
            'grau.instrucao',
            u'Grau de Instrução',
            required=True),
        'is_handicapped': fields.boolean(u'PCD - Pessoa Com Deficiência?'),
        'handicap_description': fields.text(u'Descrever a deficiência'),
        'mora_com': fields.boolean(u'Mora com o titular?'),
        'age': fields.function(
            _calculate_age,
            method=True,
            type='integer',
            string='Age'),
    }


class hr_parentesco(osv.Model):
    _name = 'hr.parentesco'
    _description = 'Parentesco'

    _columns = {
        'name': fields.char(
            'Parentesco',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('hr_parentesco_unique', 'unique(name)', u'Parentesco já existe.'),
    ]


class conselho_regional(osv.Model):
    _name = 'conselho.regional'
    _description = 'Conselho Regional'

    _columns = {
        'name': fields.char(
            'Conselho Regional',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('conselho_regional_unique',
         'unique(name)',
         u'Conselho regional já existe.'),
    ]


class orgao_expedidor(osv.Model):
    _name = 'orgao.expedidor'
    _description = u'Órgão Expedidor'

    _columns = {
        'name': fields.char(
            u'Órgão Expedidor',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('orgao_expedidor_unique',
         'unique(name)',
         u'Órgão expedidor já existe.'),
    ]


class categoria_habilitacao(osv.Model):
    _name = 'categoria.habilitacao'
    _description = u'Categoria Habilitação'

    _columns = {
        'name': fields.char(
            u'Categoria',
            size=128,
            required=True,
            translate=True),
    }

    _sql_constraints = [
        ('categoria_habilitacao_unique',
         'unique(name)',
         u'Categoria habilitação já existe.'),
    ]


class hr_employee_transportation_card(osv.Model):
    _name = 'hr.employee.transportation.card'
    _description = u'Cartão Transporte'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'name': fields.char(u'Cartão Transporte', size=64),
        'tipo_cartao_id': fields.many2one('hr.employee.transp.card', u'Tipo'),
        'valor_cartao_transp': fields.float(u'Valor'),
    }


class hr_employee_transp_card(osv.Model):
    _name = 'hr.employee.transp.card'
    _description = u'Tipo Cartão'

    _columns = {
        'name': fields.char(u'Tipo', size=128, required=True, translate=True),
    }

    _sql_constraints = [
        ('hr_employee_transp_card_unique',
         'unique(name)',
         u'Tipo de cartão já existe.'),
    ]
