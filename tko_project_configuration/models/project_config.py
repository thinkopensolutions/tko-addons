# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TaskTypeConfiguration(models.TransientModel):
    _inherit = 'project.config.settings'

    module_tko_project_task_type = fields.Boolean(string="Manage type on tasks")
    module_tko_project_task_type_stages = fields.Boolean(string="Manage task stages with task type")
    module_tko_project_task_actions = fields.Boolean(string="Manage action on tasks")
    module_tko_project_task_status = fields.Boolean(string="Manage status on tasks")
    module_tko_project_task_reviewer = fields.Boolean(string="Manage reviewer on tasks")
