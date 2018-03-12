# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    contract_sequence = fields.Char('Sequence', readonly=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code(
            'account.analytic.account') or 'New'
        vals.update({'contract_sequence': sequence})
        return super(AccountAnalyticAccount, self).create(vals)
