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


class ProjectTaskActions(models.Model):
    _name = 'project.task.status'

    name = fields.Char(string='Name', required=True)
    expected_duration = fields.Integer(u'Expected Time', required=True)
    expected_duration_unit = fields.Selection([('d', 'Day'), ('w', 'Week'), ('m', 'Month'), ('y', 'Year')],
                                              default='d', required=True, string=u'Expected Time Unit')
    filter_id = fields.Many2one('ir.filters','Filter')
    done_server_action_id = fields.Many2one('ir.actions.server', string='Done Server Rule', help=u'This server action will be executed when Actions is set to done')
    cancel_server_action_id = fields.Many2one('ir.actions.server', string='Cancel Server Rule', help=u'This server action will be executed when Actions is set to cancel')


class ProjectTaskActionsLine(models.Model):
    _name = 'project.task.status.line'

    status_id = fields.Many2one('project.task.status', u'Actions')
    expected_date = fields.Date(u'Expected Date')
    done_date = fields.Date(u'Done Date', readonly=True)
    task_id = fields.Many2one('project.task', 'Task')
    state = fields.Selection([('i', u'In Progress'), ('d', u'Done'), ('c', u'Cancelled')], default='i', required=True,
                             string='State')


    def set_done(self):
        if self.status_id.filter_id:
            #validate filter here
            self.write({'state': 'd', 'done_date':fields.Date.today()})
        if self.status_id.done_server_action_id:
            self.status_id.done_server_action_id.run()


    def set_cancel(self):
        self.state = 'c'
        if self.status_id.cancel_server_action_id:
            self.status_id.cancel_server_action_id.run()


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
            self.expected_date = datetime.today() + relativedelta(years=years, months=months, weeks=weeks, days=days)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    status_line_ids = fields.One2many('project.task.status.line', 'task_id', 'Actions')
