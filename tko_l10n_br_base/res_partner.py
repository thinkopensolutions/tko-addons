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

from datetime import date, datetime

from openerp.osv import osv, fields

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


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_is_company(self, cr, uid, ids, name, arg, context=None):
        result = {}
        convert = {True: 'j', False: 'f',}
        for partner in self.browse(cr, uid, ids, context=context):
            result[partner.id] = convert[partner.is_company]
        return result

    def _save_is_company(self, cr, uid, id, name, value, arg, context=None):
        result = {}
        convert = {'j': True, 'f': False,}
        return convert[value]

    def _age(self, birth_date):
        now = date.today()
        age_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        age = now.year - age_date.year - (
        0 if (now.month > age_date.month or (now.month == age_date.month and now.day >= age_date.day)) else 1)
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
        'is_company_selection': fields.function(
            _get_is_company,
            fnct_inv=_save_is_company,
            method=True,
            required=True,
            translate=True,
            type='selection',
            selection=IS_COMPANY,
            string=u'Main'),
        'pabx': fields.char('Phones', size=32),
        'pabx_extension': fields.char('Extension', size=32),
        'fax': fields.char('FAX', size=32),
        'fax_extension': fields.char('Extension', size=32),
        'residence_phone': fields.char('Residence', size=32),
        'gender': fields.selection(GENDER, 'Gender', translate=True),
        'district_id': fields.many2one('district', 'District'),
        'zone': fields.selection(AVAILABLE_ZONES, 'Zona', translate=True),
        'is_matriz': fields.selection(IS_MATRIZ, 'Unidade', translate=True),
        'activity_branch_id': fields.many2one('activity_branch', 'Activity Branch'),
        'business_size_id': fields.many2one('business_size', 'Business Size'),
        'annual_income_id': fields.many2one('annual_income', 'Annual Income'),
        'economic_sector_id': fields.many2one('economic_sector', 'Economic Sector'),
        'business_nationality_id': fields.many2one('business_nationality', 'Business Nationality'),
        'skype': fields.char('Skype', size=128),
        'blog': fields.char('Blog', size=256),
        'facebook': fields.char('Facebook', size=128),
        'twitter': fields.char('Twitter', size=128),
        'linkedin': fields.char('LinkedIn', size=128),
        'departamento': fields.char('Departamento', size=128),
        'birth_date': fields.date('Birthdate'),
        'age': fields.function(_calculate_age, method=True, type='integer', string='Age'),
    }

    def onchange_is_company_selection(self, cr, uid, ids, is_company_selection, context=None):
        if is_company_selection:
            return {'value': {
                'is_company': self._save_is_company(cr, uid, id, 'is_company_selection', is_company_selection, '',
                                                    context)},
                    'domain': {'title': [('is_fisica', '=', 'f')]}
                    }
        else:
            return True

    _defaults = {
        'is_matriz': 'f',
        'is_company_selection': 'f',
        'country_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid,
                                                                                 c).company_id.country_id.id,
        'state_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.state_id.id,
        'l10n_br_city_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid,
                                                                                      c).company_id.l10n_br_city_id.id,
    }


class district(osv.osv):
    _name = "district"
    _description = "District"
    _order = "name"

    _columns = {
        'name': fields.char('District', size=128, required=True, translate=True),
    }


class activity_branch(osv.osv):
    _name = "activity_branch"
    _description = "Activity Branch"

    _columns = {
        'name': fields.char('Activity Branch', size=128, required=True, translate=True),
    }


class business_size(osv.osv):
    _name = "business_size"
    _description = "Business Size"

    _columns = {
        'name': fields.char('Business Size', size=128, required=True, translate=True),
    }


class annual_income(osv.osv):
    _name = "annual_income"
    _description = "Annual Income"

    _columns = {
        'name': fields.char('Annual Income', size=128, required=True, translate=True),
    }


class economic_sector(osv.osv):
    _name = "economic_sector"
    _description = "Economic Sector"

    _columns = {
        'name': fields.char('Economic Sector', size=128, required=True, translate=True),
    }


class business_nationality(osv.osv):
    _name = "business_nationality"
    _description = "Business Nationality"

    _columns = {
        'name': fields.char('Business nationality', size=128, required=True, translate=True),
    }


class res_partner_title(osv.osv):
    _inherit = "res.partner.title"

    _columns = {
        'is_fisica': fields.boolean('Pessoa Fisica'),
        'is_juridica': fields.boolean('Pessoa Juridica'),
    }
