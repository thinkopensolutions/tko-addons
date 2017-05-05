# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class task_type(models.Model):
    _inherit = 'task.type'

    action_line_ids = fields.Many2many('project.task.action', 'project_task_type_action_rel', 'type_id', 'action_id',
                                       'Action')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    related_action_line_ids = fields.Many2many('project.task.action', 'project_task_action_rel', 'task_id', 'action_id',
                                               related='task_type_id.action_line_ids', string='Action')
