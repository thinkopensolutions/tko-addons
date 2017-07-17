# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _


class ActionLineWizard(models.TransientModel):
    _name = 'action.line.wizard'

    user_id = fields.Many2one('res.users', string='User', required=True)

    @api.multi
    def set_user(self):
        active_ids = self.env.context.get('active_ids', [])
        self.env['project.task.action.line'].browse(active_ids).write({'user_id': self.user_id.id})
        return True
