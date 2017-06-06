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

import re
from datetime import date, datetime

from openerp import _
#from openerp import api
from openerp import api
from openerp import fields, models

try:
    from openerp.addons.l10n_br_base.tools import fiscal
except:
    pass
from openerp.exceptions import Warning
# from openerp.osv import osv, fields

AVAILABLE_ZONES = [
    ('n', 'Norte'),
    ('s', 'Sul'),
    ('c', 'Centro'),
    ('l', 'Leste'),
    ('o', 'Oeste')
]

IS_COMPANY = [
    ('f', u'Pessoa Física'),
    ('j', u'Pessoa Jurídica'),
]

IS_MATRIZ = [
    ('f', 'Filial'),
    ('m', 'Matriz'),
]

GENDER = [
    ('m', 'Masculino'),
    ('f', 'Feminino'),
]


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _get_is_company(self):
        result = {}
        convert = {True: 'j', False: 'f',}
        for partner in self:
            result[partner.id] = convert[partner.is_company]
        return result
    
    @api.multi
    def _save_is_company(self, name, value, arg):
        result = {}
        convert = {'j': True, 'f': False,}
        return convert[value]

    @api.multi
    def _age(self, birth_date):
        now = date.today()
        age_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        age = now.year - age_date.year - (0 if (now.month > age_date.month or (
            now.month == age_date.month and now.day >= age_date.day)) else 1)
        return age
    @api.multi
    def _calculate_age(self):
        res = {}
        for partner in self:
            if partner.birth_date:
                partner.age = self._age(partner.birth_date)
            else:
                res[partner.id] = 0
        # return res
    # is_company_selection = fields.Selection(
    #         compute=_get_is_company,
    #         fnct_inv=_save_is_company,
    #         method=True,
    #         required=True,
    #         translate=True,
    #         selection=IS_COMPANY,
    #         string=u'Matrizn' ,default="f")

    is_company_selection = fields.Selection(
            fnct_inv=_save_is_company,
            method=True,
            required=True,
            translate=True,
            selection=IS_COMPANY,
            string=u'Matrizn' ,default="f")
    pabx = fields.Char('Phones', size=32)
    pabx_extension = fields.Char('Extension', size=32)
    fax = fields.Char('FAX', size=32)
    fax_extension = fields.Char('Extension', size=32)
    residence_phone = fields.Char('Residence', size=32)
    gender = fields.Selection(GENDER, 'Gender', translate=True)
    district_id = fields.Many2one('district', 'District')
    zone = fields.Selection(AVAILABLE_ZONES, 'Zona', translate=True)
    is_matriz = fields.Selection(IS_MATRIZ, 'Unidade', translate=True, default='f')
    activity_branch_id = fields.Many2one('activity_branch', 'Activity Branch')
    business_size_id = fields.Many2one('business_size', 'Business Size')
    annual_income_id = fields.Many2one('annual_income', 'Annual Income')
    economic_sector_id = fields.Many2one('economic_sector', 'Economic Sector')
    business_nationality_id = fields.Many2one('business_nationality', 'Business Nationality')
    skype = fields.Char('Skype', size=128)
    blog = fields.Char('Blog', size=256)
    facebook = fields.Char('Facebook', size=128)
    twitter = fields.Char('Twitter', size=128)
    linkedin = fields.Char('LinkedIn', size=128)
    departamento = fields.Char('Departamento', size=128)
    birth_date = fields.Date('Birthdate')
    age = fields.Integer(compute='_calculate_age', method=True, type='integer', string='Age')
    
    @api.onchange('is_company_selection')
    def onchange_is_company_selection(self):
        if self.is_company_selection:
            return {
                'value': {
                    'is_company': self._save_is_company(
                        'is_company_selection',
                        self.is_company_selection,
                        '')},
                'domain': {
                    'title': [
                        ('is_fisica',
                         '=',
                         'f')]}}
        else:
            return {}

    @api.onchange('cnpj_cpf', 'is_company')
    def onchange_mask_cnpj_cpf(self):
        if self.cnpj_cpf:
            if self.is_company:
                if not fiscal.validate_cnpj(self.cnpj_cpf):
                    raise Warning(_('CNPJ not valid'))
            elif not fiscal.validate_cpf(self.cnpj_cpf):
                raise Warning(_('CPF not valid'))
        return {}

    @api.onchange('email')
    def onchange_email(self):
        if self.email:
            if not re.match(
                    "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                    self.email) != None:
                raise Warning(_('Email not validated'))
        return {'value': {'email': self.email}}

    # _defaults = {
    #     'is_matriz': 'f',
    #     'is_company_selection': 'f',
    #     'country_id': lambda self,
    #                          cr,
    #                          uid,
    #                          c: self.pool.get('res.users').browse(
    #         cr,
    #         uid,
    #         uid,
    #         c).company_id.country_id.id,
    #     'state_id': lambda self,
    #                        cr,
    #                        uid,
    #                        c: self.pool.get('res.users').browse(
    #         cr,
    #         uid,
    #         uid,
    #         c).company_id.state_id.id,
    #     'l10n_br_city_id': lambda self,
    #                               cr,
    #                               uid,
    #                               c: self.pool.get('res.users').browse(
    #         cr,
    #         uid,
    #         uid,
    #         c).company_id.l10n_br_city_id.id,
    # }


class district(models.Model):
    _name = "district"
    _description = "District"
    _order = "name"

    name = fields.Char(
            'District',
            size=128,
            required=True,
            translate=True)


class activity_branch(models.Model):
    _name = "activity_branch"
    _description = "Activity Branch"


    name = fields.Char(
            'Activity Branch',
            size=128,
            required=True,
            translate=True)


class business_size(models.Model):
    _name = "business_size"
    _description = "Business Size"


    name = fields.Char(
            'Business Size',
            size=128,
            required=True,
            translate=True)

class annual_income(models.Model):
    _name = "annual_income"
    _description = "Annual Income"

    name = fields.Char(
            'Annual Income',
            size=128,
            required=True,
            translate=True)


class economic_sector(models.Model):
    _name = "economic_sector"
    _description = "Economic Sector"


    name = fields.Char(
            'Economic Sector',
            size=128,
            required=True,
            translate=True)



class business_nationality(models.Model):
    _name = "business_nationality"
    _description = "Business Nationality"


    name = fields.Char(
            'Business nationality',
            size=128,
            required=True,
            translate=True)

class res_partner_title(models.Model):
    _inherit = "res.partner.title"

    is_fisica = fields.Boolean('Pessoa Fisica')
    is_juridica = fields.Boolean('Pessoa Juridica')

