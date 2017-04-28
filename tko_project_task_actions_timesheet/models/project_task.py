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

from odoo import models, api, fields, _

class ProjectTaskActions(models.Model):
    _inherit = 'project.task.action'

    estimated_time = fields.Integer("Estimated Time")
    is_wizard_open = fields.Boolean("Is Open Wizard")

class ProjectTaskActionsLine(models.Model):
    _inherit = 'project.task.action.line'

    @api.onchange('action_id')
    def onchange_action(self):
        res = super(ProjectTaskActionsLine, self).onchange_action()
        self.estimated_time = self.action_id.estimated_time
        return res

    @api.multi
    def calculate_spent_time(self):
        for action_line in self:
            account_analytic_ids = self.env['account.analytic.line'].search([('action_id','=',action_line.id)])
            total_time = 0.0
            for timesheet in account_analytic_ids:
                total_time += timesheet.unit_amount
            action_line.spent_time = total_time

    @api.multi
    def get_palanned_hour(self):
        for action_line in self:
            if (action_line.estimated_time > 0.0):
                action_line.progress_time = round((100.0 * action_line.spent_time) / action_line.estimated_time)

    @api.multi
    def calculate_remaining_time(self):
        for action_line in self:
            action_line.remaining_time = action_line.estimated_time - action_line.spent_time
            
    estimated_time = fields.Float(string="Estimated Time")
    spent_time = fields.Float(compute='calculate_spent_time', string="Time Spent")
    remaining_time = fields.Float(compute='calculate_remaining_time', string="Remaining Time")
    progress_time = fields.Float(compute='get_palanned_hour', string='Progress', group_operator="avg")
    state = fields.Selection([('n', u'New'),('i', u'In Progress'), ('d', u'Done'), ('c', u'Cancelled')], default='i', required=True,
                             string='State')
    is_open = fields.Boolean(related="action_id.is_wizard_open")


    @api.multi
    def open_wizard(self):
        if self.action_id.is_wizard_open:
            return {
                'name': _('Timesheet Time'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timesheet.time',
                'view_id': self.env.ref('tko_project_task_actions_timesheet.timesheet_time_view').id,
                'type': 'ir.actions.act_window',
                'context': self._context,
                'target': 'new'
            }

    def set_done(self):
        super(ProjectTaskActionsLine, self).set_done()
        if self.action_id.is_wizard_open:
            return {
                'name': _('Timesheet Time'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timesheet.time',
                'view_id': self.env.ref('tko_project_task_actions_timesheet.timesheet_time_view').id,
                'type': 'ir.actions.act_window',
                'context': self._context,
                'target': 'new'
            }

    def set_cancel(self):
        super(ProjectTaskActionsLine, self).set_cancel()
        if self.action_id.is_wizard_open:
            return {
                'name': _('Timesheet Time'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timesheet.time',
                'view_id': self.env.ref('tko_project_task_actions_timesheet.timesheet_time_view').id,
                'type': 'ir.actions.act_window',
                'context': self._context,
                'target': 'new'
            }        

class Timesheet_time(models.Model):
    _name = 'timesheet.time'

    time = fields.Float("Time")

    @api.multi
    def add_time(self):
        if self._context.get('active_model')=='project.task.action.line':
            action_line = self.env['project.task.action.line'].search([('id','=',self._context.get('active_id',False))])
            timesheet_obj = self.env['account.analytic.line']
            if action_line and action_line.task_id and action_line.task_id.project_id:
                timesheet_obj.create({'name':action_line.action_id and action_line.action_id.name or '',
                                'unit_amount':self.time,'account_id':action_line.task_id.project_id.id,
                                'task_id':action_line.task_id.id,
                                'project_id':action_line.task_id.project_id.id,
                                'action_id':action_line.id  or False})

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    action_id = fields.Many2one('project.task.action.line',string='Action')
