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

import logging
import openerp
from openerp.osv import fields, osv, orm
import pytz
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import *
from openerp.addons.base.ir.ir_cron import _intervalTypes
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.http import request
from openerp.tools.translate import _
from openerp import http
import werkzeug.contrib.sessions
from openerp.http import Response

_logger = logging.getLogger(__name__)


class Home_tkobr(openerp.addons.web.controllers.main.Home):
    
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        openerp.addons.web.controllers.main.ensure_db()
        multi_ok = True
        calendar_set = 0
        calendar_ok = False
        calendar_group = ''
        unsuccessful_message = ''
        now = datetime.now()
        
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        
        if not request.uid:
            request.uid = openerp.SUPERUSER_ID
            
        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect
        
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None
            
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = False
            if request.params.has_key('login') and request.params.has_key('password'):
                uid = request.session.authenticate(request.session.db,
                    request.params['login'], request.params['password'])
            if uid is not False:
                user = request.registry.get('res.users').browse(request.cr,
                    request.uid, uid, request.context)
                if not uid is SUPERUSER_ID:
                    # check for multiple sessions block
                    sessions = request.registry.get('ir.sessions').search(request.cr,
                        request.uid,
                        [('user_id', '=', uid),
                         ('logged_in', '=', True)],
                        context=request.context)
                    
                    if sessions and user.multiple_sessions_block:
                        multi_ok = False
                    
                    if multi_ok:
                        # check calendars
                        calendar_obj = request.registry.get('resource.calendar')
                        attendance_obj = request.registry.get('resource.calendar.attendance')
                        
                        # GET USER LOCAL TIME
                        tz = pytz.timezone(user.tz)
                        tzoffset = tz.utcoffset(now)
                        now = now + tzoffset
                        
                        if user.login_calendar_id:
                            calendar_set += 1
                            # check user calendar
                            attendances = attendance_obj.search(request.cr,
                                request.uid, [('calendar_id', '=', user.login_calendar_id.id),
                                              ('dayofweek', '=', str(now.weekday())),
                                              ('hour_from', '<=', now.hour+now.minute/60.0),
                                              ('hour_to', '>=', now.hour+now.minute/60.0)],
                                context=request.context)
                            if attendances:
                                calendar_ok = True
                            else:
                                unsuccessful_message = "unsuccessful login from '%s', user time out of allowed calendar defined in user" % request.params['login']
                        else:
                            # check user groups calendar
                            for group in user.groups_id:
                                if group.login_calendar_id:
                                    calendar_set += 1
                                    attendances = attendance_obj.search(request.cr,
                                        request.uid, [('calendar_id', '=', group.login_calendar_id.id),
                                                      ('dayofweek', '=', str(now.weekday())),
                                                      ('hour_from', '<=', now.hour+now.minute/60.0),
                                                      ('hour_to', '>=', now.hour+now.minute/60.0)],
                                        context=request.context)
                                    if attendances:
                                        calendar_ok = True
                                    else:
                                        calendar_group = group.name
                                if sessions and group.multiple_sessions_block and multi_ok:
                                    multi_ok = False
                                    unsuccessful_message = "unsuccessful login from '%s', multisessions block defined in group '%s'" % (request.params['login'], group.name)
                                    break
                            if calendar_set > 0 and calendar_ok == False:
                                unsuccessful_message = "unsuccessful login from '%s', user time out of allowed calendar defined in group '%s'" % (request.params['login'], calendar_group)
                    else:
                        unsuccessful_message = "unsuccessful login from '%s', multisessions block defined in user" % request.params['login']
            else:
                unsuccessful_message = "unsuccessful login from '%s', wrong username or password" % request.params['login']
            if not unsuccessful_message or uid is SUPERUSER_ID:
                self.save_session(request.cr, uid, user.tz,
                    request.httprequest.session.sid, context=request.context)
                return http.redirect_with_hash(redirect)
            user = request.registry.get('res.users').browse(request.cr,
                SUPERUSER_ID, SUPERUSER_ID, request.context)
            self.save_session(request.cr, uid, user.tz,
                request.httprequest.session.sid, unsuccessful_message, request.context)
            _logger.info(unsuccessful_message)
            request.uid = old_uid
            values['error'] = 'Login failed due to one of the following reasons:'
            values['reason1'] = '- Wrong login/password'
            values['reason2'] = '- User not allowed to have multiple logins'
            values['reason3'] = '- User not allowed to login at this specific time or day'
        return request.render('web.login', values)
    
    def save_session(self, cr, uid, tz, sid, unsuccessful_message='', context=None):
        now = fields.datetime.now()
        session_obj = request.registry.get('ir.sessions')
        user = request.registry.get('res.users').browse(request.cr,
            request.uid, uid, request.context)
        ip = request.httprequest.headers.environ['REMOTE_ADDR']
        logged_in = True
        if unsuccessful_message:
            uid = SUPERUSER_ID
            logged_in = False
            sessions = False
        else:
            sessions = session_obj.search(cr, uid, [('session_id', '=', sid),
                                                    ('ip', '=', ip),
                                                    ('user_id', '=', uid),
                                                    ('logged_in', '=', True)],
                                          context=context)
        if not sessions:
            values = {
                      'user_id': uid,
                      'logged_in': logged_in,
                      'session_id': sid,
                      'session_seconds': user.session_default_seconds,
                      'multiple_sessions_block': user.multiple_sessions_block,
                      'date_login': now,
                      'expiration_date': datetime.strftime((datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(seconds=user.session_default_seconds)), DEFAULT_SERVER_DATETIME_FORMAT),
                      'ip': ip,
                      'remote_tz': tz,
                      'unsuccessful_message': unsuccessful_message,
                      }
            session_obj.create(cr, uid, values, context=context)
        return True
     
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True, logout_type='ul')
        return werkzeug.utils.redirect(redirect, 303)
     
