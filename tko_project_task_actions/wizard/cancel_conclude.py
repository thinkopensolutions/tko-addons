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

class ActionLinesCancel(models.TransientModel):
    _name = "action.lines.cancel"

    @api.multi
    def cancel_lines(self):
        line_obj = self.env['project.task.action.line']
        active_ids = self._context.get('active_ids')
        print
        for active_id in active_ids:
            line = line_obj.browse(active_id)
            line.with_context(active_id = active_id).set_cancel()
        return True

class ActionLinesConclude(models.TransientModel):
    _name = "action.lines.conclude"

    @api.multi
    def conclude_lines(self):
        line_obj = self.env['project.task.action.line']
        active_ids = self._context.get('active_ids')
        for active_id in active_ids:
            line = line_obj.browse(active_id)
            line.with_context(active_id = active_id).set_done()
        return True