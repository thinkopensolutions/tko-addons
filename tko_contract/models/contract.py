# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def create(self, vals):
        if 'analytic_account_type' in vals.keys() and vals['analytic_account_type'] == 'c':
            sequence = self.env['ir.sequence'].next_by_code(
                'account.analytic.account') or 'New'
            vals.update({'code': sequence})
        return super(AccountAnalyticAccount, self).create(vals)

