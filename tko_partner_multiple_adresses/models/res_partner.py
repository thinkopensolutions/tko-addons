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

import logging
import re

_logger = logging.getLogger(__name__)


class PartnerAddressType(models.Model):
    _name = 'partner.address.type'

    name = fields.Char('Name')
    type = fields.Selection([('w', u'Work'), ('r', u'Residential')], string=u'Type')


class PartnerAddressStatus(models.Model):
    _name = 'partner.address.status'

    name = fields.Char('Name')
    type = fields.Selection([('a', u'Active'), ('i', u'Inactive')], string=u'Status')


class PartnerAddress(models.Model):
    _name = 'partner.address'

    partner_id = fields.Many2one('res.partner', u'Partner')
    name = fields.Char('Address', compute='_get_address')
    zip = fields.Char(u'Zip')
    street = fields.Char(u'Street')
    street2 = fields.Char(u'Street2')
    number = fields.Char(u'Number')
    district = fields.Char(u'District')
    country_id = fields.Many2one('res.country', u'Country',
                                 default=lambda self: self.env.user.company_id.country_id.id or False)
    state_id = fields.Many2one('res.country.state', u'State')
    city_id = fields.Many2one('res.state.city', u'City')
    type_id = fields.Many2one('partner.address.type', u'Type')
    status_id = fields.Many2one('partner.address.status', u'Status')
    is_main = fields.Boolean('Is Main ?')

    @api.one
    @api.depends('zip', 'street', 'street2', 'number', 'district', 'state_id', 'city_id')
    def _get_address(self):
        address = ''
        if self.street:
            address = address + self.street
        if self.number:
            address = address + ', ' + self.number
        if self.street2:
            address = address + ', ' + self.street2
        if self.district:
            address = address + ', ' + self.district
        if self.city_id:
            address = address + ', ' + self.city_id.name
        if self.state_id:
            address = address + ', ' + self.state_id.code
        if self.zip:
            address = address + ' - ' + self.zip

        self.name = address

    @api.multi
    def set_main_address(self):
        for record in self:
            addresses = self.search([('partner_id', '=', record.partner_id.id)])
            addresses.write({'is_main': False})
            record.write({'is_main': 't'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class ResPartner(models.Model):
    _inherit = "res.partner"

    address_ids = fields.One2many('partner.address', 'partner_id', string=u'Emails')
