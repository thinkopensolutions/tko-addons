# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_id = fields.Many2one('res.partner', related='move_id.partner_id', string='Partner', store=True)
    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True, readonly=False)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', store=True, readonly=False)
