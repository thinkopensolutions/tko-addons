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


class ProjectTaskActions(models.Model):
    _name = 'project.task.action'

    name = fields.Char(string='Name', required=True)
    expected_duration = fields.Integer(u'Expected Time', default=1, required=True)
    expected_duration_unit = fields.Selection([('d', 'Day'), ('w', 'Week'), ('m', 'Month'), ('y', 'Year')],
                                              default='d', required=True, string=u'Expected Time Unit')
    filter_id = fields.Many2one('ir.filters','Filter')
    done_server_action_id = fields.Many2one('ir.actions.server', string='Done Server Rule', help=u'This server action will be executed when Actions is set to done')
    cancel_server_action_id = fields.Many2one('ir.actions.server', string='Cancel Server Rule', help=u'This server action will be executed when Actions is set to cancel')


class ProjectTaskActionsLine(models.Model):
    _name = 'project.task.action.line'

    action_id = fields.Many2one('project.task.action', u'Actions')
    expected_date = fields.Date(u'Expected Date')
    done_date = fields.Date(u'Done Date', readonly=True)
    task_id = fields.Many2one('project.task', 'Task')
    state = fields.Selection([('i', u'In Progress'), ('d', u'Done'), ('c', u'Cancelled')], default='i', required=True,
                             string='State')

    #Validate action filter
    def validate_action_filter(self):
        """

        Context must have active_id
        :return:
        """
        model_name = 'project.task'
        eval_context = self._eval_context()
        active_id = self.task_id.id
        if active_id and model_name:
            domain = self.action_id.filter_id
            rule = expression.normalize_domain(safe_eval(domain, eval_context))
            Query = self.env[model_name].sudo()._where_calc(rule, active_test=False)
            from_clause, where_clause, where_clause_params = Query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''
            query_str = 'SELECT id FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            result = self._cr.fetchall()
            if active_id in [id[0] for id in result]:
                return True
        return False

    def set_done(self):
        if self.action_id.filter_id:
            # validate filter here
            if self.validate_action_filter():
                #set to done and execute server action
                self.write({'state': 'd', 'done_date':fields.Date.today()})
                if self.action_id.done_server_action_id:
                    self.action_id.done_server_action_id.run()

    def set_cancel(self):
        self.state = 'c'
        if self.action_id.cancel_server_action_id:
            self.action_id.cancel_server_action_id.run()


    @api.onchange('action_id')
    def onchange_action(self):
        if self.action_id:
            days = weeks = months = years = 0
            if self.action_id.expected_duration_unit == 'd':
                days = self.action_id.expected_duration
            if self.action_id.expected_duration_unit == 'w':
                weeks = self.action_id.expected_duration
            if self.action_id.expected_duration_unit == 'm':
                months = self.action_id.expected_duration
            if self.action_id.expected_duration_unit == 'y':
                years = self.action_id.expected_duration
            self.expected_date = datetime.today() + relativedelta(years=years, months=months, weeks=weeks, days=days)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    action_line_ids = fields.One2many('project.task.action.line', 'task_id', 'Actions')
