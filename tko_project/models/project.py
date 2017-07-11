# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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


class ProjectSLA(models.Model):
    _name = 'project.sla'

    name = fields.Char(u'Name')
    sla_days = fields.Integer(u'SLA Days')
    sla_days_urgent = fields.Integer(u'Urgent SLA Days')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sla_id = fields.Many2one('project.sla', 'SLA')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_urgent = fields.Selection([('y', 'YES'), ('n', 'NO')], string=u'Is Urgent')
    sla_days = fields.Integer(u'SLA Days', compute='_get_sla_days')

    @api.one
    @api.depends('is_urgent', 'project_id.sla_id.sla_days', 'project_id.sla_id.sla_days_urgent')
    def _get_sla_days(self):
        if self.is_urgent == 'y':
            self.sla_days = self.project_id.sla_id.sla_days
        elif self.is_urgent == 'n':
            self.sla_days = self.project_id.sla_id.sla_days_urgent
        else:
            self.sla_days = 0

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        result = {'value': {},
                  'domain': {}}
        project_ids = []
        if self.partner_id:
            if self.partner_id.parent_id:
                partners = self.partner_id.parent_id.child_ids.ids
                partners.append(self.partner_id.parent_id.id)
            else:
                partners = self.child_ids.ids

            partners.append(self.partner_id.id)
            project_ids = self.env['project.project'].search([('partner_id', 'in', partners)]).ids
        result['domain'].update({'project_id': [('id', 'in', project_ids), ('active', '=', True)]})
        return result
