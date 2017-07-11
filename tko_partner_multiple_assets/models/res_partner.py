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

_logger = logging.getLogger(__name__)


class PartnerAssetType(models.Model):
    _name = 'partner.asset.type'

    name = fields.Char(u'Name', required=True)


class ResPartnerAsset(models.Model):
    _name = 'res.partner.asset'

    name = fields.Char('Name', compute='_get_asset_name')
    type_id = fields.Many2one('partner.asset.type', u'Type')
    value = fields.Float('Email')
    address_id = fields.Many2one('partner.address', u'Address')
    partner_id = fields.Many2one('res.partner', u'Partner')
    is_main = fields.Boolean('Is Main', help="Main Phone/Celular", default=False)


    # Set address to same Partner
    @api.model
    def create(self, vals):
        result = super(ResPartnerAsset, self).create(vals)
        if result.partner_id and result.address_id and not result.address_id.partner_id:
            result.address_id.partner_id = result.partner_id.id
        return result



    @api.one
    @api.depends('type_id', 'value', 'address_id')
    def _get_asset_name(self):
        self.name = '%s / %s / %s' %(self.type_id.name or '', self.value, self.address_id.city_id.name or '')


    @api.multi
    def set_main_asset(self):
        for record in self:
            email_ids = self.search([('partner_id', '=', record.partner_id.id)])
            email_ids.write({'is_main': False})
            vals = {'is_main': 't'}
            record.partner_id.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class ResPartner(models.Model):
    _inherit = "res.partner"

    asset_ids = fields.One2many('res.partner.asset', 'partner_id', string=u'Assets')
