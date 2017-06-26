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

from odoo import fields, models, api, _

_status_vals = [('a', u'Active'), ('i', u'Inactive')]


class PartnerPhoneState(models.Model):
    _name = 'partner.phone.state'

    """ Status of Phone Active or Inactive"""

    name = fields.Char('Name')
    status = fields.Selection(_status_vals, default='a', string=u'Status')


class PartnerPhoneType(models.Model):
    _name = "partner.phone.type"
    _description = "Phone type"

    """ Phone Type Celular or Telefone """

    name = fields.Char('name', size=64, required=True)
    type = fields.Selection([('m', 'Celular'), ('p', 'Telefone')], string='Type')


class PartnerPhoneNumber(models.Model):
    _name = "partner.phone.number"
    _description = "partner phone numbers"
    _rec_name = "number"

    def _get_default_country(self):
        return self.env.user.company_id.country_id.id or False

    number = fields.Char('Number', size=64, required=True)
    partner_id = fields.Many2one('res.partner', string=u'Partner', ondelete="cascade")
    type_id = fields.Many2one('partner.phone.type', 'Type', required=True)
    country_id = fields.Many2one('res.country', u'Country', required=True, default=_get_default_country)
    state_id = fields.Many2one('partner.phone.state', u'State')
    status = fields.Selection(_status_vals, related='state_id.status', string=u'Status')
    is_main = fields.Boolean('Is Main', help="Main Phone/Celular", default=False)

    _order = 'number'

    _sql_constraints = [
        ('unique_phone_no',
         'unique(_partner_id,number)',
         "Phone number should be unique !"),
    ]
    _constraints = []

    @api.multi
    def set_main_phone(self):
        for record in self:
            phone_ids = self.search([('partner_id', '=', record.partner_id.id), ('type_id', '=', record.type_id.id)])
            phone_ids.write({'is_main': False})
            vals = {'is_main': 't'}
            if record.type_id.type == 'm':
                vals.update({'mobile': record.number})
            if record.type_id.type == 'p':
                vals.update({'phone': record.number})
            record.partner_id.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
