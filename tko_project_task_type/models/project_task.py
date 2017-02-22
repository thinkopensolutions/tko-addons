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

from openerp import models, api, fields

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    task_type_ids = fields.Many2many('task.type','project_task_type_task_type_rel','task_type_id','type_id', store=True, string="Task Types")

    @api.one
    def get_task_type_ids(self):
        all_task_types = self.env['task.type'].search([])
        selected_types = []
        for type in all_task_types:
            if self in type.stage_ids:
                selected_types.append(type.id)
        self.write({'task_type_ids' : [(6,0, selected_types)]})

class TaskType(models.Model):
    _name = 'task.type'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index', size=1)
    task_id = fields.Many2one('project.task', string='Task')
    stage_ids = fields.Many2many('project.task.type','task_type_task_stage_rel','type_id', 'stage_id', string='Stages')

    @api.multi
    def write(self, vals):
        stages = []
        [stages.append(stage) for stage in self.stage_ids]
        result= super(TaskType, self).write(vals)
        [stages.append(stage) for stage in self.stage_ids]
        stages = list(set(stages))
        for stage in stages:
            stage.get_task_type_ids()
        return result

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_default_stage_id(self):
        return super(ProjectTask,self)._get_default_stage_id()

    type_name = fields.Char(
        compute='_get_type_name',
        store=True,
        string='Name')
    task_type_id = fields.Many2one('task.type', string='Type')
    color = fields.Integer(compute='_get_color', string='Color', store=False)
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               domain="[('task_type_ids', '=', task_type_id)]", copy=False)

    @api.multi
    def name_get(self):
        result = []
        for task in self:
            task_type = task.task_type_id and task.task_type_id.name or ''
            result.append(
                (task.id, "%s %s" %
                 ('[' + task_type + ']', task.name or ' ')))
        return result

    @api.depends('task_type_id.name')
    def _get_type_name(self):
        for record in self:
            if record.task_type_id:
                record.type_name = record.task_type_id.name

    @api.depends('task_type_id.color')
    def _get_color(self):
        for record in self:

            if record.task_type_id:
                record.color = record.task_type_id.color

    @api.onchange('task_type_id')
    def _change_task_type(self):
        if self.task_type_id:
            self.color = str(self.task_type_id.color)[-1]
            self.type_name = self.task_type_id.name
