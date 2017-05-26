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


class crm_claim(models.Model):
    _inherit = 'crm.claim'

    function = fields.Char(string='Function', related='partner_id.function')
    function_id = fields.Many2one('curriculum.job.position', string='Function', compute='get_partner_function',
                                  inverse='set_partner_function')

    @api.onchange('function_id')
    def onchange_function(self):
        if self.function_id:
            self.function = self.function_id.name
        else:
            self.function = False

    @api.depends('partner_id')
    @api.one
    def get_partner_function(self):
        if self.partner_id:
            self.function_id = self.partner_id.function_id.id
            self.function = self.partner_id.function_id.name

    @api.multi
    def set_partner_function(self):
        self.ensure_one()
        if self.partner_id and self.function_id:
            self.partner_id.write({'function_id': self.function_id.id, 'function': self.function_id.name})

    @api.onchange('parent_id', 'function_id')
    def onchange_company(self):
        res = {}
        for record in self:
            if record.parent_id and not record.function_id:

                if self.env.user.company_id.claim_company_domain:
                    partners = self.env['res.partner'].search([('parent_id', '=', record.parent_id.id)])
                    res['domain'] = {'partner_id': [('id', 'in', [partner.id for partner in partners])]}
                record.company_phone = record.parent_id.phone
                record.company_website = record.parent_id.website
                record.company_email = record.parent_id.email
            elif not record.parent_id and record.function_id:
                partners = self.env['res.partner'].search([('function_id', '=', record.function_id.id)])
                res['domain'] = {'partner_id': [('id', 'in', [partner.id for partner in partners])]}
            elif record.parent_id and record.function_id:
                partners = self.env['res.partner'].search(
                    [('function_id', '=', record.function_id.id), ('parent_id', '=', record.parent_id.id)])
                res['domain'] = {'partner_id': [('id', 'in', [partner.id for partner in partners])]}
                record.company_phone = record.parent_id.phone
                record.company_website = record.parent_id.website
                record.company_email = record.parent_id.email
            else:
                res['domain'] = {'partner_id': [('id', 'not in', [])]}
        return res
