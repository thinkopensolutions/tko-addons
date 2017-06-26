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

_status_vals  = [('a', u'Active'), ('i', u'Inactive')]
class PartnerPhoneState(models.Model):
    _name = 'partner.phone.state'
    name = fields.Char('Name')
    status = fields.Selection(_status_vals, default ='a', string=u'Status')

class PartnerPhoneType(models.Model):
    _name = "partner.phone.type"
    _description = "Phone type"

    name = fields.Char('Type', size=64, required=True)
    code = fields.Char('Code', size=64, required=True, readonly=False)

class PartnerPhoneNumber(models.Model):
    _name = "partner.phone.number"
    _description = "partner phone numbers"
    _rec_name = "phone"

    def _get_default_country(self):
        return 23

    phone = fields.Char('Number', size=64, required=True)
    partner_id = fields.Many2one('res.partner', string=u'Partner', ondelete="cascade")
    type_id = fields.Many2one('partner.phone.type', 'Type', required=True)
    country_id = fields.Many2one('res.country', u'Country', required=True, default=_get_default_country)
    state_id = fields.Many2one('partner.phone.state', u'State')
    status = fields.Selection(_status_vals, related='state_id.status', string=u'Status')
    is_main = fields.Boolean('Is Main', help="Main Phone/Celular", default=False)

    _order = 'phone'

    _sql_constraints = [
        ('unique_phone_no',
         'unique(_partner_id,phone)',
         "Phone number should be unique !"),
    ]
    _constraints = []

    # def set_partner_phone(self, cr, uid, ids, context=None):
    #      = {}
    #     for record in self.browse(cr, uid, ids):
    #         phone_ids = self.search(
    #             cr, uid, [
    #                 ('_partner_id', '=', record._partner_id.id), ('type_id', '=', record.type_id.id)])
    #         self.write(cr, uid, phone_ids, {'is_active': False})
    #         self.write(cr, uid, ids, {'is_active': 't'})
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }


