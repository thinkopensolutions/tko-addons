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

from datetime import datetime
from dateutil.relativedelta import *

from odoo.addons.base.ir.ir_cron import _intervalTypes
from odoo.http import request
from odoo import  fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class res_users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _check_session_validity(self, db, uid, passwd):
        if not request:
            return
        now = fields.datetime.now()
        session = request.session
        if session.db and session.uid:
            session_obj = request.env['ir.sessions']
            cr = self.pool.cursor()
            # autocommit: our single update request will be performed atomically.
            # (In this way, there is no opportunity to have two transactions
            # interleaving their cr.execute()..cr.commit() calls and have one
            # of them rolled back due to a concurrent access.)
            cr.autocommit(True)
            session_ids = session_obj.search([('session_id', '=', session.sid),
                              ('date_expiration', '>', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                              ('logged_in', '=', True)], order='date_expiration asc')
            if session_ids:
                if request.httprequest.path[:5] == '/web/' or \
                                request.httprequest.path[:9] == '/im_chat/' or \
                                request.httprequest.path[:6] == '/ajax/':
                    open_sessions = session_ids.read(['logged_in',
                                                      'date_login',
                                                      'session_seconds',
                                                      'date_expiration'])
                    for s in open_sessions:
                        session_id = session_obj.browse(s['id'])
                        date_expiration = (now + relativedelta(seconds=session_id.session_seconds)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        session_duration = str(now - datetime.strptime(
                                        session_id.date_login,
                                        DEFAULT_SERVER_DATETIME_FORMAT)).split('.')[0]
                        cr.execute('UPDATE ir_sessions '\
                                   'SET date_expiration=%s, '\
                                   'session_duration=%s '\
                                   'WHERE id= %s', (date_expiration,
                                                session_duration,
                                                session_id.id,))
                    cr.commit()
            else:
                session.logout(logout_type='to', keep_db=True)
            cr.close()
        return True

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(res_users, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        self = api.Environment(cr, uid, {})[cls._name]
        cr.commit()
        cr.close()
        self.browse(uid)._check_session_validity(db, uid, passwd)
        return res

    @api.depends('interval_number','interval_type','groups_id.interval_number','groups_id.interval_type')
    def _get_session_default_seconds(self):
        now = datetime.now()
        seconds = (now + _intervalTypes['weeks'](1) - now).total_seconds()
        for user in self:
            if user.interval_number and user.interval_type:
                u_seconds = (
                    now +
                    _intervalTypes[
                        user.interval_type](
                        user.interval_number) -
                    now).total_seconds()
                if u_seconds < seconds:
                    seconds = u_seconds
            else:
                # Get lowest session time
                for group in user.groups_id:
                    if group.interval_number and group.interval_type:
                        g_seconds = (
                            now +
                            _intervalTypes[
                                group.interval_type](
                                group.interval_number) -
                            now).total_seconds()
                        if g_seconds < seconds:
                            seconds = g_seconds
            user.session_default_seconds = seconds

    login_calendar_id = fields.Many2one('resource.calendar',
                                         'Allowed Login Calendar', company_dependent=True,
                                         help='The user will be only allowed to login in the calendar defined here.\nNOTE:The calendar defined here will overlap all defined in groups.')
    multiple_sessions_block = fields.Boolean('Block Multiple Sessions', company_dependent=True, default=False,
                                              help='Select this to prevent user to start more than one session.')
    interval_number = fields.Integer('Default Session Duration', company_dependent=True,
                                      help='This is the timeout for this user.\nNOTE: The timeout defined here will overlap all the timeouts defined in groups.')
    interval_type  = fields.Selection([('minutes', 'Minutes'),
                                       ('hours', 'Hours'), ('work_days', 'Work Days'),
                                       ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                      'Interval Unit', company_dependent=True)
    session_default_seconds = fields.Integer(compute=_get_session_default_seconds,
                                               string='Session Seconds',)
    session_ids = fields.One2many('ir.sessions', 'user_id', 'User Sessions')
    ip = fields.Char(related='session_ids.ip', string='Latest ip adress')

