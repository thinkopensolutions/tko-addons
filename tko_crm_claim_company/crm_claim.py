# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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

from openerp import models, fields, api


class res_company(models.Model):
    _inherit = 'res.company'

    claim_company_domain = fields.Boolean('Claim Company Domain')


class crm_claim(models.Model):
    _inherit = 'crm.claim'

    @api.multi
    def get_company_id(self):
        return self.env.user.company_id.id

    parent_id = fields.Many2one('res.partner', string='Company')
    company_phone = fields.Char(
        string='Phone', compute='_get_company_info', inverse='_set_company_info')
    company_website = fields.Char(
        string='Website', compute='_get_company_info', inverse='_set_company_info')
    company_email = fields.Char(
        string='Email', compute='_get_company_info', inverse='_set_company_info')

    @api.depends('partner_id')
    def _get_company_info(self):
        for record in self:
            if record.partner_id and record.partner_id.parent_id:
                record.parent_id = record.partner_id.parent_id.id
                record.company_phone = record.partner_id.parent_id.phone
                record.company_website = record.partner_id.parent_id.website
                record.company_email = record.partner_id.parent_id.email
            if record.parent_id:
                record.company_phone = record.parent_id.phone
                record.company_website = record.parent_id.website
                record.company_email = record.parent_id.email

    @api.onchange('parent_id')
    def onchange_company(self):
        res = {}
        for record in self:
            if record.parent_id:

                if self.env.user.company_id.claim_company_domain:
                    partners = self.env['res.partner'].search(
                        [('parent_id', '=', record.parent_id.id)])
                    res['domain'] = {'partner_id': [
                        ('id', 'in', [partner.id for partner in partners])]}
                record.company_phone = record.parent_id.phone
                record.company_website = record.parent_id.website
                record.company_email = record.parent_id.email
            else:
                res['domain'] = {'partner_id': [('id', 'not in', [])]}
        return res

    @api.one
    def _set_company_info(self):
        for record in self:
            if record.parent_id:
                record.parent_id.write({'phone': record.company_phone,
                                        'website': record.company_website,
                                        'email': record.company_email,
                                        })
            if record.partner_id and record.partner_id.parent_id:
                record.parent_id.write({'phone': record.company_phone,
                                        'website': record.company_website,
                                        'email': record.company_email,
                                        })
            if record.partner_id and not record.partner_id.parent_id:
                record.partner_id.write({
                    'parent_id': record.parent_id.id,
                })

    @api.onchange('partner_id', 'email')
    def onchange_partner_id(self):

        res = super(crm_claim, self).onchange_partner_id()
        if self.partner_id:
            parent_id = self.partner_id.parent_id and self.partner_id.parent_id.id or False
            res['value'].update({'parent_id': parent_id})
        return res
