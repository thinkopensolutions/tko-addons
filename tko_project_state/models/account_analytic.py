# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class accountanalyticaccount(models.Model):
    _inherit = 'account.analytic.account'

    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('pending', 'Pending'),
                              ('done', 'Done'), ('cancelled', 'Cancelled')],
                             string="State", default='draft')
