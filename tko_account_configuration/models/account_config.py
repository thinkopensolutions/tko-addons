# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountConfiguration(models.TransientModel):
    _inherit = 'account.config.settings'

    module_tko_account_moves_in_draft = fields.Boolean(string="Create account moves in draft stages in invoice")
