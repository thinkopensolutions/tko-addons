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


class task_type(models.Model):
    _inherit = 'task.type'

    status_line_ids = fields.Many2many('project.task.status', 'project_task_type_status_rel', 'type_id', 'status_id',
                                       'Status')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    related_status_line_ids = fields.Many2many('project.task.status', 'project_task_status_rel', 'task_id', 'status_id',
                                               related='task_type_id.status_line_ids', string='Status')
