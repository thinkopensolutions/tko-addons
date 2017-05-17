# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields
from datetime import datetime
from  dateutil.relativedelta import relativedelta
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import time
from odoo.exceptions import Warning


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    task_ids = fields.Many2many("project.task", "task_stage_project_task_rel", "stage_id","project_id", string="tasks")

    # add task in stage
    @api.multi
    def remove_task_from_stage(self, task):
        for task in self:
            task.task_ids = [(3, task.id)]
        return True

    # remove task from stage
    @api.multi
    def add_task_in_stage(self, task):
        for task in self:
            task.task_ids = [(4,task.id)]
        return True


class ProjectTask(models.Model):
    _inherit = 'project.task'

    action_line_ids = fields.One2many('project.task.action.line', 'task_id', 'Actions')

    @api.model
    def create(self, vals):
        task =  super(ProjectTask, self).create(vals)
        if task.stage_id:
            task.stage_id.add_task_in_stage(task)
        return task

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            for task in self:
                # remove task from stage
                task.stage_id.remove_task_from_stage(task)
                res = super(ProjectTask, task).write(vals)
                # add task to new stage
                task.stage_id.add_task_in_stage(task)
            return res
        else:
            return super(ProjectTask, self).write(vals)


    # This method is to set already
    # create tasks in stages
    @api.model
    def _set_tasks_in_stages(self):
        stages = self.env['project.task.type'].search([])
        for stage in stages:
            task_ids = self.search([('stage_id','=',stage.id)]).ids
            if len(task_ids):
                stage.task_ids = [(6, 0, task_ids)]
