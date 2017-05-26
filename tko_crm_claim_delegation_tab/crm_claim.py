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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, SUPERUSER_ID


class delegation_action(models.Model):
    _name = 'delegation.action'

    name = fields.Char('Name')
    description = fields.Text('Description')
    planned_hours = fields.Float('Initially Planned Hours')


class claim_delegation(models.Model):
    _name = 'claim.delegation'

    claim_id = fields.Many2one('crm.claim', string='Claim')
    action_id = fields.Many2one('delegation.action', string='Action', required=False)
    description = fields.Text(string='Description')
    department_id = fields.Many2one('hr.department', string='Department')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True)
    delegated_date = fields.Datetime('Delegated Date', readonly=True)
    finished_date = fields.Datetime('Finished Date', readonly=True)
    state = fields.Selection([('n', 'New'), ('a', 'Assigned'), ('d', 'Done'), ('c', 'Cancelled')], default='n',
                             string='State', readonly=True)
    date_deadline = fields.Datetime('Deadline', readonly=False)
    warning_mail = fields.Boolean('Sent Warning Mail')
    last_notified = fields.Date(
        'Last Notified Date')  # this field is used to notify manager of department if delegation is expired

    @api.onchange('action_id')
    def action_changed(self):
        if self.action_id:
            self.description = self.action_id.description

    @api.model
    def create(self, vals):
        res = super(claim_delegation, self).create(vals)
        if 'action_id' in vals.keys():
            user = self.env['res.users'].browse(SUPERUSER_ID)
            user_tz = user.partner_id.tz
            if user_tz:
                # less timezone difference
                todays = datetime.now() - timedelta(hours=3)  # datetime.now(pytz.timezone(user_tz))
            else:
                todays = datetime.now() - timedelta(hours=3)
            whole_days = int(res.action_id.planned_hours / 9)
            remaining_hours = res.action_id.planned_hours % 9
            weekday = todays.weekday()
            # TODO: timezone difference should not be rigid
            deadline = todays + timedelta(days=whole_days, hours=remaining_hours)  # timezone difference
            # fix time exeeded than 18 hours
            if deadline.hour >= 18 and deadline.minute > 0 or deadline.hour < 9:
                deadline = deadline + relativedelta(hours=15)  # (24-18)EVE + MOR(9-0) = 15

            # fix days if falling on saturday or sunday
            if deadline.weekday() == 5 or deadline.weekday() == 6:
                deadline = deadline = deadline + relativedelta(days=2)
            res.write({'date_deadline': deadline + timedelta(hours=3)})
        return res

    @api.one
    def write(self, vals):
        res = super(claim_delegation, self).write(vals)
        if 'action_id' in vals.keys():
            user = self.env['res.users'].browse(SUPERUSER_ID)
            user_tz = user.partner_id.tz
            if user_tz:
                # less timezone difference
                todays = datetime.now() - timedelta(hours=3)  # datetime.now(pytz.timezone(user_tz))
            else:
                todays = datetime.now() - timedelta(hours=3)
            whole_days = int(self.action_id.planned_hours / 9)
            remaining_hours = self.action_id.planned_hours % 9
            weekday = todays.weekday()
            # TODO: timezone difference should not be rigid
            deadline = todays + timedelta(days=whole_days, hours=remaining_hours)  # timezone difference
            # fix time exeeded than 18 hours
            if deadline.hour >= 18 and deadline.minute > 0 or deadline.hour < 9:
                deadline = deadline + relativedelta(hours=15)  # (24-18)EVE + MOR(9-0) = 15

            # fix days if falling on saturday or sunday
            if deadline.weekday() == 5 or deadline.weekday() == 6:
                deadline = deadline = deadline + relativedelta(days=2)
            self.write({'date_deadline': deadline + timedelta(hours=3)})
        return res

    @api.model
    def last_day_warning_mail(self):
        ''' This method commits after each mail is drafted'''
        # get all delegations in new or assigned state and have not warned
        delegations = self.search([('state', 'not in', ['d', 'c']), ('warning_mail', '!=', True)])
        for delegation in delegations:
            deadline = datetime.strptime(delegation.date_deadline, "%Y-%m-%d %H:%M:%S").date()
            # calculate difference between deadline and today's date
            diff = (deadline - datetime.today().date()).days
            partners = []
            if diff < 2:
                if delegation.user_id:
                    partners = [delegation.user_id.partner_id.id]
                elif delegation.department_id:
                    employees = self.env['hr.employee'].search([('department_id', '=', delegation.department_id.id)])
                    users = [emp.user_id for emp in employees]
                    # remove False values "employess without users"
                    partners = [user.partner_id.id for user in users if users]
            # create and send mail
            if partners:
                # append partner in list of recipients
                manager = delegation.user_id and delegation.user_id and delegation.user_id.partner_id.id or False
                if manager and manager not in partners:
                    partners.append(manager)

                vals = {
                    'state': 'outgoing',
                    'subject': 'Action %s assigned to %s with deadline %s' % (
                    delegation.action_id.name, delegation.user_id.name, delegation.date_deadline),
                    'body_html': 'Hi, Action %s assigned to %s with deadline %s' % (
                    delegation.action_id.name, delegation.user_id.name or None, delegation.date_deadline),
                    'email_to': False,
                    'recipient_ids': [(6, False, partners)],
                    'email_from': delegation.user_id.email,
                }
                mail_obj = self.env['mail.mail']
                mail = mail_obj.create(vals)
                mail_obj.send(mail)
                # set warning mail True for don't send it again by scheduler
                delegation.write({'warning_mail': True})
                # coommit after each mail is sent
                self.env.cr.commit()
        return True

    @api.model
    def expired_warning_mail(self):
        ''' This method commits after each mail is drafted'''
        # get all delegations in new or assigned state and have not warned
        delegations = self.search([('state', 'not in', ['d', 'c'])])
        for delegation in delegations:
            deadline = datetime.strptime(delegation.date_deadline, "%Y-%m-%d %H:%M:%S").date()
            # calculate difference between deadline and today's date
            diff = (deadline - datetime.today().date()).days
            partners = []
            if diff < 0 and delegation.last_notified and datetime.strptime(delegation.last_notified,
                                                                           "%Y-%m-%d").date() < datetime.today().date():
                # get manager
                if delegation.user_id and delegation.user_id and delegation.user_id.partner_id:
                    partners = [delegation.user_id.partner_id.id]

            # create and send mail
            if len(partners):
                vals = {
                    'state': 'outgoing',
                    'subject': 'Action %s assigned to %s with deadline %s' % (
                    delegation.action_id.name, delegation.user_id.name, delegation.date_deadline),
                    'body_html': 'Hello %s, Action %s assigned to %s with deadline %s Has been expired' % (
                    delegation.user_id.partner_id.name, delegation.action_id.name, delegation.user_id.name or None,
                    delegation.date_deadline),
                    'email_to': False,
                    'recipient_ids': [(6, False, partners)],
                    'email_from': delegation.user_id.email,
                }
                mail_obj = self.env['mail.mail']
                mail = mail_obj.create(vals)
                mail_obj.send(mail)
                # set warning mail True for don't send it again by scheduler
                delegation.write({'last_notified': datetime.now()})
                # coommit after each mail is sent
                self.env.cr.commit()
        return True
        # ===========================================================================

    # #considered business hours from 6 - 9 monday to friday
    # @api.onchange('action_id')
    # def action_change(self):
    #     user = self.env['res.users'].browse(SUPERUSER_ID)
    #     user_tz = user.partner_id.tz
    #     if user_tz:
    #         #less timezone difference
    #         todays = datetime.now() - timedelta(hours = 3) # datetime.now(pytz.timezone(user_tz))
    #     else:
    #         todays = datetime.now()
    #     whole_days = int(self.action_id.planned_hours / 9)
    #     remaining_hours = self.action_id.planned_hours % 9
    #     weekday = todays.weekday()
    #     #TODO: timezone difference should not be rigid
    #     deadline = todays + timedelta(days = whole_days, hours = remaining_hours) #timezone difference
    #     #fix time exeeded than 18 hours
    #     if deadline.hour >= 18  and deadline.minute > 0 or deadline.hour < 9:
    #         deadline = deadline + relativedelta(hours=15) # (24-18)EVE + MOR(9-0) = 15 
    #     
    #     #fix days if falling on saturday or sunday
    #     if deadline.weekday() == 5:
    #         deadline = deadline = deadline + relativedelta(days=2)
    #     if deadline.weekday() == 6:
    #         deadline = deadline = deadline + relativedelta(days=1)
    #     print "dead.line.......",deadline,  todays, deadline.hour
    #     self.planned_hours = self.action_id.planned_hours
    #     self.date_deadline = deadline + timedelta(hours = 3) #add timezone difference
    # ===========================================================================

    # delegate action and send mails to whole department
    @api.one
    def delegate_me(self):
        old_state = self.state
        self.write({
            'state': 'a',
            'user_id': self.env.uid,
            'delegated_date': datetime.now(),
        })
        # send mail to everyone in department
        # send mail only if state is changed from new to assigned
        if old_state == 'n':
            if self.department_id:
                employees = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
                users = [emp.user_id for emp in employees if emp.user_id != False]
                # remove False values "employess without users"
                partners = [user.partner_id.id for user in users]
            else:
                partners = [self.env.user.partner_id.id]

            vals = {
                'state': 'outgoing',
                'subject': 'Action %s assigned to %s with deadline %s' % (
                self.action_id.name, self.user_id.name, self.date_deadline),
                'body_html': 'Hi there Action assined for %s' % (self.claim_id.name),
                'email_to': False,
                'recipient_ids': [(6, False, partners)],
                'email_from': self.user_id.email,
            }
            mail_obj = self.env['mail.mail']
            mail = mail_obj.create(vals)
            mail_obj.send(mail)

    @api.one
    def set_done(self):
        if self.state == 'a':
            self.write({
                'state': 'd',
                'finished_date': datetime.now(),
            })

    @api.one
    def set_cancel(self):
        self.write({
            'state': 'c',
            'finished_date': datetime.now(),
        })


class crm_claim(models.Model):
    _inherit = 'crm.claim'

    delegation_ids = fields.One2many('claim.delegation', 'claim_id', string='Delegation')
