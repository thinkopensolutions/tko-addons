# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CrmSchedulePhonecall(models.TransientModel):
    _name = "crm.schedule_phonecall"

    name = fields.Char('Call Summary', required=True)
    date = fields.Datetime('Date', required=True)
    name = fields.Char('Call summary', required=True, index=True)
    user_id = fields.Many2one('res.users', "Assign To")
    partner_phone = fields.Char('Phone')
    partner_mobile = fields.Char('Mobile')
    team_id = fields.Many2one('crm.team', 'Sales Team')
    partner_id = fields.Many2one('res.partner', "Partner")
    opportunity_id = fields.Many2one('crm.lead', 'opportunity')

    @api.multi
    def action_schedule(self):
        Phonecall = self.env['crm.phonecall']

        phonecall_to_cancel_id = self._context.get('phonecall_to_cancel')
        if phonecall_to_cancel_id:
            phonecall_to_cancel = Phonecall.browse(phonecall_to_cancel_id)
            phonecall_to_cancel.write({
                'state': 'cancel',
                'in_queue': False,
            })
        Phonecall.create({
            'name': self.name,
            'user_id': self.user_id.id,
            'date': self.date,
            'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'partner_phone': self.partner_phone,
            'partner_mobile': self.partner_mobile,
            'opportunity_id': self.opportunity_id.id,
        })
