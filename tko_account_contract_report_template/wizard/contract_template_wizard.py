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

from openerp import models, api, fields, _


class contract_template_wizard(models.TransientModel):
    _name = 'contract.template.wizard'
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    partner_phone = fields.Char(string='Phone')
    partner_mobile = fields.Char(string='Mobile')
    partner_email = fields.Char(string='Email')
    partner_country_id = fields.Many2one('res.country', string='Country')
    partner_state_id = fields.Many2one('res.country.state', string='State')
    partner_city = fields.Char(string='City')
    partner_street = fields.Char(string='Street')
    partner_street2 = fields.Char(string='Street2')
    partner_zip = fields.Char(string='Zip', size=24)
    manager_id = fields.Many2one('res.users', string='Account Manager', required=True)
    manager_phone = fields.Char(string='Phone')
    manager_mobile = fields.Char(string='Mobile')
    manager_email = fields.Char(string='Email')
    manager_country_id = fields.Many2one('res.country', string='Country')
    manager_state_id = fields.Many2one('res.country.state', string='State')
    manager_city = fields.Char(string='City')
    manager_street = fields.Char(string='Street')
    manager_street2 = fields.Char(string='Street2')
    manager_zip = fields.Char(string='Zip', size=24)
    manager_function = fields.Char(string='Job Position')
    company_id = fields.Many2one('res.partner', string='Company', required=True)
    company_phone = fields.Char(string='Phone')
    company_mobile = fields.Char(string='Mobile')
    company_email = fields.Char(string='Email')
    company_country_id = fields.Many2one('res.country', string='Country')
    company_state_id = fields.Many2one('res.country.state', string='State')
    company_city = fields.Char(string='City')
    company_street = fields.Char(string='Street')
    company_street2 = fields.Char(string='Street2')
    company_zip = fields.Char(string='Zip', size=24)
    signature = fields.Binary('Signature')
    contract_template_id = fields.Many2one('account.analytic.account.contract.report.body',
       string='Contract', required=True)
   
    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        data = {}
        # assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        active_id = context.get('active_id', False)
        contract_obj = self.pool.get('account.analytic.account').browse(cr, uid, active_id)
        
        if active_id:
            data['partner_id'] = contract_obj.partner_id and contract_obj.partner_id.id or False
            data['partner_phone'] = contract_obj.partner_id.phone or False
            data['partner_mobile'] = contract_obj.partner_id.mobile or False
            data['partner_email'] = contract_obj.partner_id.email or False
            data['partner_country_id'] = contract_obj.partner_id.country_id.id or False
            data['partner_state_id'] = contract_obj.partner_id.state_id.id or False
            data['partner_city'] = contract_obj.partner_id.city or False
            data['partner_street'] = contract_obj.partner_id.street or False
            data['partner_street2'] = contract_obj.partner_id.street2 or False
            data['partner_zip'] = contract_obj.partner_id.zip or False
            data['manager_id'] = contract_obj.manager_id and contract_obj.manager_id.id or False
            data['manager_phone'] = contract_obj.manager_id.phone or False
            data['manager_mobile'] = contract_obj.manager_id.mobile or False
            data['manager_email'] = contract_obj.manager_id.email or False
            data['manager_country_id'] = contract_obj.manager_id.country_id.id or False
            data['manager_state_id'] = contract_obj.manager_id.state_id.id or False
            data['manager_city'] = contract_obj.manager_id.city or False
            data['manager_street'] = contract_obj.manager_id.street or False
            data['manager_street2'] = contract_obj.manager_id.partner_id.street2 or False
            data['manager_zip'] = contract_obj.manager_id.zip or False
            data['manager_function'] = contract_obj.manager_id.function or False
            data['company_id'] = contract_obj.company_id.partner_id and contract_obj.company_id.partner_id.id or False
            data['company_phone'] = contract_obj.company_id.partner_id.phone or False
            data['company_mobile'] = contract_obj.company_id.partner_id.mobile or False
            data['company_email'] = contract_obj.company_id.partner_id.email or False
            data['company_country_id'] = contract_obj.company_id.partner_id.country_id.id or False
            data['company_state_id'] = contract_obj.company_id.partner_id.state_id.id or False
            data['company_city'] = contract_obj.company_id.partner_id.city or False
            data['company_street'] = contract_obj.company_id.partner_id.street or False
            data['company_street2'] = contract_obj.company_id.partner_id.street2 or False
            data['company_zip'] = contract_obj.company_id.partner_id.zip or False
            if contract_obj.contract_template_body_id:
                data['signature'] = contract_obj.contract_template_body_id.signature
                data['contract_template_id'] = contract_obj.contract_template_body_id.id
        return data
    
    @api.onchange('contract_template_id')
    def change_contemplate(self):
        self.signature = self.contract_template_id.signature
        
    def print_contract(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]
        active_ids = context.get('active_ids', [])
        wizard_obj = self.browse(cr, uid, ids[0])
        contract_obj = self.pool.get('account.analytic.account')
        report_body_obj = self.pool.get('account.analytic.account.contract.report.body')
        part_obj = self.pool.get('res.partner')
        
        # write contract fields  values to respective fields
        contract_obj.write(cr, uid, active_ids, {
            'partner_id': wizard_obj.partner_id.id,
            'manager_id': wizard_obj.manager_id.id,
            'company_id': wizard_obj.company_id.id,
            'contract_template_body_id': wizard_obj.contract_template_id.id,
            })
        
        # write partner field values
        part_obj.write(cr, uid, [wizard_obj.partner_id.id], {
            'phone': wizard_obj.partner_phone,
            'mobile': wizard_obj.partner_mobile,
            'email': wizard_obj.partner_email,
            'country_id': wizard_obj.partner_country_id.id,
            'state_id': wizard_obj.partner_state_id.id,
            'city': wizard_obj.partner_city,
            'street2': wizard_obj.partner_street2,
            'zip': wizard_obj.partner_zip,
            })
        
        # write manager related fields
        part_obj.write(cr, uid, [wizard_obj.manager_id.partner_id.id], {
            'phone': wizard_obj.manager_phone,
            'mobile': wizard_obj.manager_mobile,
            'email': wizard_obj.manager_email,
            'country_id': wizard_obj.manager_country_id.id,
            'state_id': wizard_obj.manager_state_id.id,
            'city': wizard_obj.manager_city,
            'street': wizard_obj.manager_street,
            'street2': wizard_obj.manager_street2,
            'zip': wizard_obj.manager_zip,
            'function': wizard_obj.manager_function,
            })
        
        # write company field values
        part_obj.write(cr, uid, [wizard_obj.company_id.id], {
            'phone': wizard_obj.company_phone,
            'mobile': wizard_obj.company_mobile,
            'email': wizard_obj.company_email,
            'country_id': wizard_obj.company_country_id.id,
            'state_id': wizard_obj.company_state_id.id,
            'city': wizard_obj.company_city,
            'street': wizard_obj.company_street,
            'street2': wizard_obj.company_street2,
            'zip': wizard_obj.company_zip,
            })
        
        report_body_obj.write(cr, uid, [wizard_obj.contract_template_id.id], {'signature': wizard_obj.signature})
        
        return contract_obj.generate_contract(cr, uid, active_ids, context=context)
    
