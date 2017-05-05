# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
