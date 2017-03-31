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

from odoo import fields, models

class TaskTypeConfiguration(models.TransientModel):
    _inherit = 'project.config.settings'

    module_tko_project_task_type = fields.Boolean(string="Manage type on tasks")
    module_tko_project_task_type_stages = fields.Boolean(string="Manage task stages with task type")
    module_tko_project_task_actions = fields.Boolean(string="Manage action on tasks")
    module_tko_project_task_status = fields.Boolean(string="Manage status on tasks")
    module_tko_project_task_reviewer = fields.Boolean(string="Manage reviewer on tasks")