# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from openerp.exceptions import ValidationError


class ProjectTaskActions(models.Model):
    _inherit = 'project.task.action'

    user_id = fields.Char(string="Assigned To")


class ProjectTaskActionsLine(models.Model):
    _inherit = 'project.task.action.line'

    user_id = fields.Many2one('res.users', string="Assigned To", compute='onchange_action', store=True)

    @api.one
    @api.depends('action_id')
    def onchange_action(self):
        res = super(ProjectTaskActionsLine, self).onchange_action()
        flag = False
        user_id = False
        try:
            user_id = self and self.task_id and self.task_id.project_id and self.action_id and self.action_id.user_id and eval(
                'self.' + self.action_id.user_id) or False
        except Exception as e:
            flag = True
        if (user_id and user_id._name != 'res.users') or flag:
            raise ValidationError("Please set proper user id in " + self.action_id.name)
        self.user_id = user_id and user_id.id or []


class ProjectTask(models.Model):
    _inherit = 'project.task'

    user_ids = fields.Many2many('res.users', string='Envolved', compute='get_users')

    @api.multi
    def get_users(self):
        user_ids = []
        for action_line in self.action_line_ids:
            if action_line.user_id:
                user_ids.append(action_line.user_id.id)
        self.user_ids = [(6, 0, list(set(user_ids)))]
