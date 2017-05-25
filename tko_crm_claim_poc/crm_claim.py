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
from openerp import fields, models, api


class calendar_phonecall(models.Model):
    _inherit = 'crm.phonecall'

    claim_poc_id = fields.Many2one('res.partner', 'Contact')

    @api.onchange('claim_poc_id')
    def change_claim_poc_id(self):
        self.partner_id = self.claim_poc_id.id

    @api.onchange('claim_id')
    def change_claim_id(self):
        res = super(calendar_phonecall, self).change_claim_id()
        partner_ids = []
        if self.claim_id:
            if self.claim_id.partner_id:
                partner_ids.append(self.claim_id.partner_id.id)
                for child in self.claim_id.partner_id.child_ids:
                    partner_ids.append(child.id)

            res['domain'] = {'claim_poc_id': [('id', 'in', partner_ids)]}
        self.claim_poc_id = self.claim_id.partner_id.id
        self.partner_id = self.claim_id.partner_id.id
        self.poc_function_id = self.claim_id.partner_id.function_id.id
        self.poc_function_id2 = self.claim_id.partner_id.function_id.id
        return res


class crm_claim(models.Model):
    _inherit = 'crm.claim'

    claim_poc_id = fields.Many2one('res.partner', 'POC')
    poc_partner_function = fields.Char('Function', related='claim_poc_id.function', readonly=True)
    poc_function_id = fields.Many2one('curriculum.job.position', string='Function', compute='get_poc_function_id',
                                      inverse='set_poc_function_id')
    poc_function_id2 = fields.Many2one('curriculum.job.position', string='Function')
    poc_partner_mobile = fields.Char(string='Mobile', compute='_get_poc_partner_info', inverse='_set_poc_partner_info')
    poc_partner_phone = fields.Char(string='Phone', compute='_get_poc_partner_info', inverse='_set_poc_partner_info')
    poc_partner_email = fields.Char(string='Email', compute='_get_poc_partner_email', inverse='_set_poc_partner_email')
    poc = fields.Boolean('Use Point of Contact')

    @api.depends('claim_poc_id')
    @api.one
    def get_poc_function_id(self):
        if self.claim_poc_id:
            self.poc_function_id = self.claim_poc_id.function_id.id
        else:
            self.poc_function_id = self.poc_function_id2.id

    @api.one
    def set_poc_function_id(self):
        self.poc_function_id2 = self.poc_function_id.id
        if self.claim_poc_id:
            self.claim_poc_id.write({'function_id': self.poc_function_id.id})

    @api.depends('claim_poc_id')
    def _get_poc_partner_info(self):
        for record in self:
            if record.claim_poc_id:
                record.poc_partner_phone = record.claim_poc_id.phone
                record.poc_partner_mobile = record.claim_poc_id.mobile
                record.poc_partner_email = record.claim_poc_id.email

    @api.depends('claim_poc_id')
    def _get_poc_partner_email(self):
        for record in self:
            if record.claim_poc_id:
                record.poc_partner_email = record.claim_poc_id.email

    def _set_poc_partner_info(self):
        if self.claim_poc_id:
            self.claim_poc_id.write({'phone': self.poc_partner_phone,
                                     'mobile': self.poc_partner_mobile,
                                     })

    def _set_poc_partner_email(self):
        if self.claim_poc_id:
            self.claim_poc_id.email = self.poc_partner_email

    def onchange_partner_id(self, cr, uid, ids, partner_id, email=False, context=None):

        res = super(crm_claim, self).onchange_partner_id(cr, uid, ids, partner_id, email=email, context=context)
        if partner_id:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner_obj.relative_ids:
                for relative in partner_obj.relative_ids:
                    res['value'].update({'claim_poc_id': relative.id})
            else:
                res['value'].update({'claim_poc_id': False})

        return res
