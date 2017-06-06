# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import odoo
from odoo import api, fields, models, tools


class CrmPhonecall(models.Model):
    _name = "crm.phonecall"

    _order = "sequence, id"

    name = fields.Char('Call Summary', required=True)
    date = fields.Datetime('Date', default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.uid)
    partner_id = fields.Many2one('res.partner', 'Contact')
    company_id = fields.Many2one('res.company', 'Company')
    description = fields.Text('Description')
    duration = fields.Float('Duration', help="Duration in minutes and seconds.")
    partner_phone = fields.Char('Phone')
    partner_mobile = fields.Char('Mobile')
    team_id = fields.Many2one('crm.team', 'Sales Team', index=True,
        default=lambda self: self.env['crm.team']._get_default_team_id(self.env.uid),
        help="Sales team to which Case belongs to.")
    in_queue = fields.Boolean('In Call Queue', default=True)
    sequence = fields.Integer('Sequence', index=True,
        help="Gives the sequence order when displaying a list of Phonecalls.")
    start_time = fields.Integer("Start time")
    state = fields.Selection([
        ('pending', 'Not Held'),
        ('cancel', 'Cancelled'),
        ('open', 'To Do'),
        ('done', 'Held'),
        ], string='Status', default='open', track_visibility='onchange',
        help='The status is set to To Do, when a case is created.\n'
             'When the call is over, the status is set to Held.\n'
             'If the call is not applicable anymore, the status can be set to Cancelled.')
    opportunity_id = fields.Many2one('crm.lead', 'Lead/Opportunity',
        ondelete='cascade', track_visibility='onchange')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
            self.partner_mobile = self.partner_id.mobile

    @api.onchange('opportunity_id')
    def _onchange_opportunity(self):
        if self.opportunity_id:
            self.team_id = self.opportunity_id.team_id
            self.partner_id = self.opportunity_id.partner_id
            self.partner_phone = self.opportunity_id.phone\
                or self.partner_id.phone
            self.partner_mobile = self.opportunity_id.mobile\
                or self.partner_id.mobile

    @api.multi
    def schedule_another_phonecall(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'key2': 'client_action_multi',
            'src_model': "crm.phonecall",
            'res_model': "crm.schedule_phonecall",
            'multi': "True",
            'target': 'new',
            'context': {
                'phonecall_to_cancel': self.id,
                'default_name': self.name,
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
                'default_opportunity_id': self.opportunity_id.id,
                'default_partner_phone': self.partner_phone,
                'default_partner_mobile': self.partner_mobile,
                'default_team_id': self.team_id.id,
            },
            'views': [[False, 'form']],
        }

    @api.multi
    def action_button_to_opportunity(self):
        self.ensure_one()
        if not self.opportunity_id:
            self.opportunity_id = self.env['crm.lead'].create({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'phone': self.partner_phone,
                'mobile': self.partner_mobile,
                'team_id': self.team_id.id,
                'description': self.description,
                'type': 'opportunity',
                'email_from': self.partner_id.email,
            })
        return self.opportunity_id.redirect_opportunity_view()