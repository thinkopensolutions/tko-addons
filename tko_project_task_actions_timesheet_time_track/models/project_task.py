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

from datetime import datetime

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProjectTaskActionsLine(models.Model):
    _inherit = 'project.task.action.line'

    @api.multi
    def _calculate_current_action_time(self):
        for obj in self:
            if obj.date_start_timer:
                obj.current_time = (datetime.now() - datetime.strptime(obj.date_start_timer,
                                                                       DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() / 60.0 / 60.0
            else:
                obj.current_time = False
        return True

    timer_user_id = fields.Many2one('res.users', 'User')
    date_start_timer = fields.Datetime('Time Start Job');
    current_time = fields.Float('Current Time Job', compute="_calculate_current_action_time");

    @api.multi
    def button_start_timer(self):
        reload = False
        for obj in self:
            action_ids = obj.env['project.task.action.line'].search([('date_start_timer', '!=', False),
                                                                     ('timer_user_id', '=', obj.env.user.id)])
            for action in action_ids:
                action.button_stop_timer()
                reload = True
            if obj.state == 'n':
                obj.state = 'i'
            obj.timer_user_id = obj.env.user
            obj.date_start_timer = datetime.now()
        if reload:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return True

    @api.multi
    def button_stop_timer(self):
        for obj in self:
            if obj.timer_user_id == obj.env.user:
                if obj.date_start_timer:
                    obj.spent_time = obj.spent_time + obj.current_time
                    obj.timer_user_id = False
                    obj.date_start_timer = False
            else:
                raise ValidationError(
                    _("You can't stop a timer of another user"))
        return True
