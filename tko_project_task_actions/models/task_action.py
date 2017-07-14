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
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DT


class ProjectTaskActions(models.Model):
    _name = 'project.task.action'

    name = fields.Char(string='Name', required=True)
    expected_type = fields.Selection([('t', 'Time'), ('d', 'Date Field')],
                                     default='d', string=u'Date Condition')
    expected_date_field_id = fields.Many2one('ir.model.fields', 'Date Field')
    expected_duration = fields.Integer(u'Expected Time', default=1)
    expected_duration_unit = fields.Selection([('d', 'Day'), ('w', 'Week'), ('m', 'Month'), ('y', 'Year')],
                                              default='d', required=True, string=u'Expected Time Unit')
    done_filter_id = fields.Many2one('ir.filters', 'Done Filter')
    done_filter_warning_message = fields.Text("Done Warning Message")
    done_server_action_id = fields.Many2one('ir.actions.server', string='Done Server Action',
                                            help=u'This server action will be executed when Actions is set to done')
    cancel_filter_id = fields.Many2one('ir.filters', 'Cancel Filter')
    cancel_filter_warning_message = fields.Text("Cancel Warning Message")
    cancel_server_action_id = fields.Many2one('ir.actions.server', string='Cancel Server Action',
                                              help=u'This server action will be executed when Actions is set to cancel')


class ProjectTaskActionsLine(models.Model):
    _name = 'project.task.action.line'

    name = fields.Char('Name', compute='_get_action_line_name')
    action_id = fields.Many2one('project.task.action', u'Actions')
    expected_date = fields.Date(u'Expected Date', compute='onchange_action', store=True)
    done_date = fields.Date(u'Done Date', readonly=True)
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade')
    state = fields.Selection([('i', u'To Do'), ('d', u'Done'), ('c', u'Cancelled')], default='i', required=True,
                             string='State')
    remaining_days = fields.Integer("Remaining Days")
    is_delayed = fields.Selection([('d', 'Delayed')])
    task_description = fields.Html(string='Description', related='task_id.description')
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for next stage'),
        ('blocked', 'Blocked')
    ], string='Kanban State',
        default='normal',
        track_visibility='onchange',
        required=True, copy=False,
        related='task_id.kanban_state',
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing the progress of this task\n"
             " * Ready for next stage indicates the task is ready to be pulled to the next stage")
    partner_id = fields.Many2one('res.partner', 'Customer', related='task_id.partner_id')
    project_id = fields.Many2one('project.project', 'Project', related='task_id.project_id')

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default['done_date'] = False
        return super(ProjectTaskActionsLine, self).copy(default)

    @api.multi
    def get_remaining_days(self):
        lines = self.search([('state', '=', 'i')])
        for line in lines:
            if line.expected_date and not line.done_date:
                days = (datetime.strptime(line.expected_date, DT).date() - datetime.today().date()).days
                line.remaining_days = days
                if days < 0:
                    line.is_delayed = 'd'
        return True

    @api.one
    def _get_action_line_name(self):
        name = ' '
        if self.action_id.name and self.task_id.name:
            name = self.action_id.name + ' - ' + self.task_id.name
        elif self.action_id.name:
            name = self.action_id.name
        elif self.task_id.name:
            name = self.task_id.name

        self.name = name

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        return {'user': self.env.user, 'time': time}

    @api.one
    @api.depends('action_id')
    def onchange_action(self):
        if self.action_id.expected_type == 't':
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
                self.expected_date = datetime.today() + relativedelta(years=years, months=months, weeks=weeks,
                                                                      days=days)
        else:
            expected_date = False
            if self.action_id.expected_date_field_id:
                expected_date = getattr(self.task_id, str(self.action_id.expected_date_field_id.name))
            self.expected_date = expected_date or datetime.today()

    # Validate action done filter
    def validate_action_done_filter(self):
        """

        Context must have active_id
        :return:
        """
        model_name = 'project.task'
        eval_context = self._eval_context()
        active_id = self.task_id.id
        if active_id and model_name:
            domain = self.action_id.done_filter_id.domain
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

    # Validate action cancel filter
    def validate_action_cancel_filter(self):
        """

        Context must have active_id
        :return:
        """
        model_name = 'project.task'
        eval_context = self._eval_context()
        active_id = self.task_id.id
        if active_id and model_name:
            domain = self.action_id.cancel_filter_id.domain
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
        if self.action_id.done_filter_id:
            # validate filter here
            if not self.validate_action_done_filter():
                raise Warning(self.action_id.done_filter_warning_message or "Warning message not set for done filter")
                # set to done and execute server action

        self.write({'state': 'd', 'done_date': fields.Date.today(), 'is_delayed': False})
        if self.action_id.done_server_action_id:
            new_context = dict(self.env.context)
            if 'active_id' not in new_context.keys():
                new_context.update({'active_id': self.id, 'active_model': 'project.task.action.line'})
            recs = self.action_id.done_server_action_id.with_context(new_context)
            recs.run()

    def set_cancel(self):
        if self.action_id.cancel_filter_id:
            # validate filter here
            if not self.validate_action_cancel_filter():
                raise Warning(
                    self.action_id.cancel_filter_warning_message or "Warning message not set for cancel filter")
        self.write({'state': 'c', 'is_delayed': False})
        if self.action_id.cancel_server_action_id:
            new_context = dict(self.env.context)
            if 'active_id' not in new_context.keys():
                new_context.update({'active_id': self.id, 'active_model': 'project.task.action.line'})
            recs = self.action_id.cancel_server_action_id.with_context(new_context)
            recs.run()
