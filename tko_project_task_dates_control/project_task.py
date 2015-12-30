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

from openerp import fields, models, api, _
from datetime import timedelta, datetime


_stage_type = [('i', 'Initial'), ('f', 'Final'), ('c', 'Cancel')]


class project_task(models.Model):
    _inherit = 'project.task'

    date_initiated = fields.Boolean('Task Initiated')

    # can't carete on_change because it method doesn't gets triggered with
    # widget="statusbar"
    @api.multi
    def write(self, vals):
        for record in self:
            res = super(project_task, self).write(vals)
            if 'stage_id' in vals:
                if record.stage_id.stage_type == 'i' and not record.date_initiated:
                    vals.update(
                        {'date_start': fields.datetime.now(), 'date_initiated': True})
                elif record.stage_id.stage_type == 'f' or record.stage_id.stage_type == 'c':
                    vals.update({'date_end': fields.datetime.now()})
                res = super(project_task, self).write(vals)
        return res

    # not working correctly , added 1 extra day to get correct date
    @api.onchange('date_deadline')
    def onchange_date_deadline(self):
        for record in self:
            if record.date_deadline:
                deadline = datetime.strptime(
                    record.date_deadline, '%Y-%m-%d') + timedelta(days=1)
                record.date_end = deadline


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    stage_type = fields.Selection(_stage_type, string='Type')
