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

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import time
import logging
_logger = logging.getLogger(__name__)


class DynamicSelection(models.Model):
    _name = 'dynamic.selection'

    name = fields.Char('Name')
    record_id = fields.Integer("Record ID")

class IrServerObjectLines(models.Model):
    _inherit = 'ir.server.object.lines'

    dynamic_selection_id = fields.Many2one('dynamic.selection', string='Dynamic Selection')

    @api.onchange('col1')
    def onchange_col1(self):
        dynamic_obj = self.env['dynamic.selection']

        col1 = self.col1
        value = self.value
        if self.col1:
            if self.col1.relation:
                records = self.env[self.col1.relation].search([])
            if self.col1.ttype in ['many2one', 'many2many']:
                dynamic_obj.search([]).unlink()
                for record in records:
                    dynamic_obj.create({'name' : record.name,
                                        'record_id': record.id})
        self.col1 = col1
        self.value = value


    @api.onchange('dynamic_selection_id')
    def onchange_dynamic_selection(self):
        if self.dynamic_selection_id:
            self.value = self.dynamic_selection_id.record_id

