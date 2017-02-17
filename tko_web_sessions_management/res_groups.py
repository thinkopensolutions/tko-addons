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

from odoo import  fields, models


class res_groups(models.Model):
    _inherit = 'res.groups'

    login_calendar_id = fields.Many2one('resource.calendar',
                                         'Allow Login Calendar', company_dependent=True,
                                         help='The user will be only allowed to login in the calendar defined here.\nNOTE: The users will be allowed to login using a merge/union of all calendars to wich one belongs.')
    multiple_sessions_block = fields.Boolean('Block Multiple Sessions', company_dependent=True,
                                              help='Select this to prevent users of this group to start more than one session.')
    interval_number = fields.Integer('Default Session Duration', company_dependent=True,
                                      help='This define the timeout for the users of this group.\nNOTE: The system will get the lowest timeout of all user groups.')
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                       ('hours', 'Hours'), ('work_days', 'Work Days'),
                                       ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                      'Interval Unit', company_dependent=True)
