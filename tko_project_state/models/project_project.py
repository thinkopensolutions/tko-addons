# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class Project(models.Model):
    _inherit = 'project.project'

    state = fields.Selection(related='analytic_account_id.state', string='Status',
                             default='draft', track_visibility='onchange', store=True)

    @api.multi
    def set_open(self):
        self.state = 'open'

    @api.multi
    def set_pending(self):
        self.state = 'pending'

    @api.multi
    def set_reopen(self):
        self.state = 'draft'

    @api.multi
    def set_done(self):
        self.state = 'done'

    @api.multi
    def set_cancelled(self):
        self.state = 'cancelled'
