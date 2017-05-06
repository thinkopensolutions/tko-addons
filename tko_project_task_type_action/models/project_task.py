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

from odoo import models, fields, api


class task_type(models.Model):
    _inherit = 'task.type'

    action_line_ids = fields.Many2many('project.task.action', 'project_task_type_action_rel', 'type_id', 'action_id',
                                       'Actions')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    related_action_line_ids = fields.Many2many('project.task.action', 'project_task_action_rel', 'task_id', 'action_id',
                                               related='task_type_id.action_line_ids', string='Action')


class ProjectTaskActionsLine(models.Model):
    _inherit = 'project.task.action.line'

    task_type_id = fields.Many2one(u'Task Type', related='task_id.task_type_id', stored=True)

    #task_type_id = fields.Many2one(u'Task Type', compute='_get_task_type', stored=True)

    #@api.depends('task_id.task_type_id')
    #def _get_task_type(self):
    #    self.task_type_id = self.task_id.task_type_id.id
    #    return True
