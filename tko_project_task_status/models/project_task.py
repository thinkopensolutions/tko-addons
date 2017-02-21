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


class ProjectTaskStatus(models.Model):
    _name = 'project.task.status'

    name = fields.Char(string='Name', required=True)
    expected_duration = fields.Integer(u'Expected Time', required=True)
    expected_duration_unit = fields.Selection([('d','Day'),('w','Week'),('m','Month'),('y','Year')], defaults='d',required=True, string=u'Expected Time Unit')


class ProjectTaskStatusLine(models.Model):
    _name = 'project.task.status.line'

    status_id = fields.Many2one('project.task.status',u'Status')
    expected_date = fields.Date(u'Expected Date')
    task_id = fields.Many2one('project.task', 'Task')

    @api.onchange('status_id')
    def onchange_status(self):
        if self.status_id:
            days = weeks = months = years = 0
            if self.status_id.expected_duration_unit == 'd':
                days = self.status_id.expected_duration
            if self.status_id.expected_duration_unit == 'w':
                weeks = self.status_id.expected_duration
            if self.status_id.expected_duration_unit == 'm':
                months = self.status_id.expected_duration
            if self.status_id.expected_duration_unit == 'y':
                years = self.status_id.expected_duration
            self.expected_date = datetime.today() + relativedelta(years=years, months=months, weeks=weeks, days =days)



class ProjectTask(models.Model):
    _inherit = 'project.task'

    status_line_ids = fields.One2many('project.task.status.line','task_id','Status')






