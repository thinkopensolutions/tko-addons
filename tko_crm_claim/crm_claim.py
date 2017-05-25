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

import calendar
import pytz
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

AVAILABLE_PRIORITIES = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3', 'High'),
]


class res_partner(models.Model):
    _inherit = 'res.partner'

    claim_ids = fields.One2many('crm.claim', 'partner_id', 'Claims')


class claim_origin(models.Model):
    _name = 'claim.origin'

    name = fields.Char('Name', required=True)


class claim_type(models.Model):
    _name = 'claim.type'

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('crm.case.categ', 'Category')
    planned_hours = fields.Float('Initially Planned Hours')
    assigned_id = fields.Many2one('res.users', 'Assigned to')
    supervisor_id = fields.Many2one('res.users', 'Supervisor')


class calendar_event(models.Model):
    _inherit = 'calendar.event'

    claim_id = fields.Many2one('crm.claim', string='Claim')
    active_model = fields.Char('Active Model', default=lambda self: self.env.context.get('active_model', False))

    # button used to save form(when it is wizard opened from claim form)
    def save_calendar_event(self, cr, uid, ids, context=None):
        return True


class calendar_phonecall(models.Model):
    _inherit = 'crm.phonecall'

    claim_id = fields.Many2one('crm.claim', string='Claim')
    active_model = fields.Char('Active Model', default=lambda self: self.env.context.get('active_model', False))

    @api.onchange('claim_id')
    def change_claim_id(self):
        res = {}
        res['value'] = {'partner_id': self.claim_id.partner_id.id}
        return res

    @api.model
    def default_get(self, fields_list):
        data = super(calendar_phonecall, self).default_get(fields_list)
        if 'default_claim_id' in self._context.keys() and self._context['default_claim_id']:
            data['partner_id'] = self.env['crm.claim'].browse(self._context['default_claim_id']).partner_id.id
        return data

    # button used to save form(when it is wizard opened from claim form)
    def save_phonecall(self, cr, uid, ids, context=None):
        return True


class crm_case_categ(models.Model):
    _inherit = 'crm.case.categ'

    assigned_id = fields.Many2one('res.users', 'Assigned to')
    supervisor_id = fields.Many2one('res.users', 'Supervisor')
    color = fields.Integer('Color', size=1)


class crm_claim(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _inherit = 'crm.claim'

    _order = "priority desc"

    # compute sequence just to show before save
    def _get_sequence(self):
        sequence_obj = self.env['ir.sequence'].search([('code', '=', 'crm.claim')])
        prefix = sequence_obj.prefix or ''
        suffix = sequence_obj.suffix or ''
        return prefix + str(format(sequence_obj.number_next_actual, '0' + str(sequence_obj.padding))) + suffix

        # return self.env['ir.sequence'].get('crm.claim')

    name = fields.Char('Protocol', default=_get_sequence)
    color = fields.Integer(string='Color', related='categ_id.color')
    partner_id = fields.Many2one('res.partner', 'Claimer')
    date_deadline = fields.Datetime('Deadline')
    countdown_timer = fields.Char(compute='_get_bussiness_hours', string='Countdown Timer')
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority')
    partner_mobile = fields.Char(string='Mobile', compute='_get_partner_info', inverse='_set_partner_info')
    partner_phone2 = fields.Char(string='Phone', compute='_get_partner_info', inverse='_set_partner_info')
    partner_email = fields.Char(string='Email', compute='_get_partner_info', inverse='_set_partner_info')
    claim_ids = fields.Many2many('crm.claim', compute='get_claim_ids', store=False)
    type_id = fields.Many2one('claim.type', 'Claim Type')
    assigned_id = fields.Many2one('res.users', 'Assigned to', compute='_get_assinged_supervisor', readonly=False,
                                  store=True)
    supervisor_id = fields.Many2one('res.users', 'Supervisor', compute='_get_assinged_supervisor', readonly=False,
                                    store=True)
    event_ids = fields.One2many('calendar.event', 'claim_id', 'Calls')
    phonecall_ids = fields.One2many('crm.phonecall', 'claim_id', 'Meetings')
    scheduled_phonecall_ids = fields.Many2many('crm.phonecall', string='Scheduled Calls', compute='get_phonecall_ids',
                                               store=False, readonly=True)
    logged_phonecall_ids = fields.Many2many('crm.phonecall', string='Logged Calls', compute='get_phonecall_ids',
                                            store=False, readonly=True)
    tag_ids = fields.Many2many('res.partner.category', string='Tags')
    origin_id = fields.Many2one('claim.origin', string='Origin')

    @api.one
    def set_high_priority(self):
        self.priority = '2'

    @api.one
    def set_normal_priority(self):
        self.priority = '0'

    @api.depends('phonecall_ids')
    def get_phonecall_ids(self):
        for record in self:
            logged_calls = []
            scheduled_calls = []
            for phonecall in record.phonecall_ids:
                if datetime.strptime(phonecall.date, DEFAULT_SERVER_DATETIME_FORMAT) > datetime.now():
                    scheduled_calls.append(phonecall.id)
                else:
                    logged_calls.append(phonecall.id)
            self.scheduled_phonecall_ids = [(6, 0, scheduled_calls)]
            self.logged_phonecall_ids = [(6, 0, logged_calls)]

    @api.depends('partner_id')
    def _get_partner_info(self):
        for record in self:
            if record.partner_id:
                record.partner_phone2 = record.partner_id.phone
                record.partner_mobile = record.partner_id.mobile
                record.partner_email = record.partner_id.email

    # somehow this method doesn't work so moving this to write
    @api.depends('partner_phone2', 'partner_mobile', 'partner_email')
    def _set_partner_info(self):
        pass
        # moved below code to wirte(), for some reason it doesn't work here
        # =======================================================================
        # if self.partner_id:
        #     self.partner_id.write({'phone': self.partner_phone2,
        #                            'mobile' :self.partner_mobile,
        #                            'email' : self.partner_email,})
        # =======================================================================

    # set correct supervisor and assinged to
    @api.depends('type_id', 'categ_id')
    @api.one
    def _get_assinged_supervisor(self):
        assigned_id = self.type_id and self.type_id.assigned_id and self.type_id.assigned_id.id or False
        supervisor_id = self.type_id and self.type_id.supervisor_id and self.type_id.supervisor_id.id or False
        if not assigned_id:
            assigned_id = self.categ_id and self.categ_id.assigned_id and self.categ_id.assigned_id.id or assigned_id

        if not supervisor_id:
            supervisor_id = self.categ_id and self.categ_id.supervisor_id and self.categ_id.supervisor_id.id or False
        self.assigned_id = assigned_id
        self.supervisor_id = supervisor_id

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].get('crm.claim')})
        res = super(crm_claim, self).create(vals)
        if 'type_id' in vals.keys():
            user = self.env['res.users'].browse(SUPERUSER_ID)
            user_tz = user.partner_id.tz
            if user_tz:
                # less timezone difference
                todays = datetime.now() - timedelta(hours=3)  # datetime.now(pytz.timezone(user_tz))
            else:
                todays = datetime.now() - timedelta(hours=3)
            whole_days = int(res.type_id.planned_hours / 9)
            remaining_hours = res.type_id.planned_hours % 9
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
        res = super(crm_claim, self).write(vals)
        # update partner related fields
        part_dict = {}
        if 'partner_phone2' in vals.keys():
            part_dict.update({'phone': vals['partner_phone2']})
        if 'partner_mobile' in vals.keys():
            part_dict.update({'mobile': vals['partner_mobile']})
        if 'partner_email' in vals.keys():
            part_dict.update({'email': vals['partner_email']})
        if part_dict:
            self.partner_id.write(part_dict)

        if 'type_id' in vals.keys():
            user = self.env['res.users'].browse(SUPERUSER_ID)
            user_tz = user.partner_id.tz
            if user_tz:
                # less timezone difference
                todays = datetime.now() - timedelta(hours=3)  # datetime.now(pytz.timezone(user_tz))
            else:
                todays = datetime.now() - timedelta(hours=3)
            whole_days = int(self.type_id.planned_hours / 9)
            remaining_hours = self.type_id.planned_hours % 9
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

    # considered business hours from 6 - 9 monday to friday
    @api.depends('date_deadline')
    @api.one
    def _get_bussiness_hours(self):
        if self.date_deadline:
            fromdate = date.today()
            todate = datetime.strptime(self.date_deadline, "%Y-%m-%d %H:%M:%S").date()
            if not todate >= fromdate:
                self.countdown_timer = '00' + ':' + '00' + ':' + '00' + ':' '00'
                return
            daygenerator = (fromdate + timedelta(x + 1) for x in xrange((todate - fromdate).days))
            weekdays = sum(1 for day in daygenerator if day.weekday() < 5) - 1

            # subtract 3 to get time of 'America/Sao_Paulo', using timezone gives wrong calculation 'America/Sao_Paulo' gives -3.1 difference instaed of -3

            user = self.env['res.users'].browse(SUPERUSER_ID)
            user_tz = user.partner_id.tz or 'UTC'
            todays = pytz.utc.localize(datetime.now()).astimezone(pytz.timezone(user_tz))

            # (9-18) + 3 hours becuase of timezone
            offset = (calendar.timegm(time.localtime()) - calendar.timegm(time.gmtime())) / 3600
            offset = -3
            start_hour = 9 - (offset)
            end_hour = 12 - (offset)

            # today's datetime obj with start time
            start = pytz.utc.localize(datetime(year=todays.year, month=todays.month, day=todays.day, hour=start_hour,
                                               minute=todays.minute)).astimezone(pytz.timezone(user_tz))
            # today's datetime obj with end time
            end = pytz.utc.localize(
                datetime(year=todays.year, month=todays.month, day=todays.day, hour=end_hour, minute=0))
            final = pytz.utc.localize(datetime.strptime(self.date_deadline, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                pytz.timezone(user_tz))
            final_day_start = pytz.utc.localize(
                datetime(year=final.year, month=final.month, day=final.day, hour=start_hour, minute=0,
                         second=0)).astimezone(pytz.timezone(user_tz))
            remaining_time_today = 0
            if end < todays:
                remaining_time_today = (end - todays).total_seconds()
            if remaining_time_today < 0:
                remaining_time_today = 0
            # remaining time on final day
            remaining_time_final_day = (final - final_day_start).total_seconds()
            diff = remaining_time_today + remaining_time_final_day

            if diff > 0:
                hours, seconds = divmod(diff, 60 * 60)
                minutes, seconds = divmod(seconds, 60)
            else:
                hours = '00'
                minutes = '00'
                seconds = '00'
            hours = str(int(hours))
            minutes = str(int(minutes))
            seconds = str(int(seconds))
            if len(str(hours)) < 2:
                hours = '0' + hours
            if len(str(minutes)) < 2:
                minutes = '0' + minutes
            if len(str(seconds)) < 2:
                seconds = '0' + seconds

            if int(weekdays) > 0 and len(str(weekdays)) < 2:
                weekdays = '0' + str(weekdays)
                self.countdown_timer = str(weekdays) + ':' + hours + ':' + minutes + ':' + seconds
            else:
                self.countdown_timer = '00:00:00:00'

    @api.depends('partner_id')
    def get_claim_ids(self):
        for record in self:
            claim_ids = []
            if record.partner_id:
                for claim in record.partner_id.claim_ids:
                    claim_ids.append(claim.id)
            self.claim_ids = [(6, 0, claim_ids)]
