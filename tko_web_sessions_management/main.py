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
import pytz
from datetime import datetime
from dateutil.relativedelta import *

import odoo
import werkzeug.contrib.sessions
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import  fields, models, _

# from odoo import pooler

_logger = logging.getLogger(__name__)


class Home_tkobr(odoo.addons.web.controllers.main.Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        if not request.registry.get('ir.sessions'):
            return super(Home_tkobr,self).web_login(redirect=redirect, **kw)
        _logger.debug('Authentication method: Home_tkobr.web_login !')
        odoo.addons.web.controllers.main.ensure_db()
        multi_ok = True
        calendar_set = 0
        calendar_ok = False
        calendar_group = ''
        unsuccessful_message = ''
        now = datetime.now()

        session_obj = request.env['ir.sessions']
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect

        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = False
            if 'login' in request.params and 'password' in request.params:
                uid = request.session.authenticate(request.session.db, request.params[
                    'login'], request.params['password'])
            if uid is not False:
                user = request.env.user
                if not uid is SUPERUSER_ID:
                    # check for multiple sessions block
                    sessions = session_obj.search(
                            [('user_id', '=', uid), ('logged_in', '=', True)])

                    if sessions and user.multiple_sessions_block:
                        multi_ok = False

                    if multi_ok:
                        # check calendars
                        calendar_obj = request.registry.get(
                            'resource.calendar')
                        attendance_obj = request.registry.get(
                            'resource.calendar.attendance')

                        # GET USER LOCAL TIME
                        if user.tz:
                            tz = pytz.timezone(user.tz)
                        else:
                            tz = pytz.timezone('GMT')
                        tzoffset = tz.utcoffset(now)
                        now = now + tzoffset

                        if user.login_calendar_id:
                            calendar_set += 1
                            # check user calendar
                            attendances = attendance_obj.search(request.cr,
                                                                request.uid,
                                                                [('calendar_id', '=', user.login_calendar_id.id),
                                                                 ('dayofweek', '=', str(now.weekday())),
                                                                 ('hour_from', '<=', now.hour + now.minute / 60.0),
                                                                 ('hour_to', '>=', now.hour + now.minute / 60.0)],
                                                                context=request.context)
                            if attendances:
                                calendar_ok = True
                            else:
                                unsuccessful_message = "unsuccessful login from '%s', user time out of allowed calendar defined in user" % \
                                                       request.params[
                                                           'login']
                        else:
                            # check user groups calendar
                            for group in user.groups_id:
                                if group.login_calendar_id:
                                    calendar_set += 1
                                    attendances = attendance_obj.search(request.cr,
                                                                        request.uid, [('calendar_id', '=',
                                                                                       group.login_calendar_id.id),
                                                                                      ('dayofweek', '=',
                                                                                       str(now.weekday())),
                                                                                      ('hour_from', '<=',
                                                                                       now.hour + now.minute / 60.0),
                                                                                      ('hour_to', '>=',
                                                                                       now.hour + now.minute / 60.0)],
                                                                        context=request.context)
                                    if attendances:
                                        calendar_ok = True
                                    else:
                                        calendar_group = group.name
                                if sessions and group.multiple_sessions_block and multi_ok:
                                    multi_ok = False
                                    unsuccessful_message = _(
                                        "unsuccessful login from '%s', multisessions block defined in group '%s'") % (
                                                               request.params['login'], group.name)
                                    break
                            if calendar_set > 0 and calendar_ok == False:
                                unsuccessful_message = _(
                                    "unsuccessful login from '%s', user time out of allowed calendar defined in group '%s'") % (
                                                           request.params['login'], calendar_group)
                    else:
                        unsuccessful_message = _("unsuccessful login from '%s', multisessions block defined in user") % \
                                               request.params[
                                                   'login']
            else:
                unsuccessful_message = _("unsuccessful login from '%s', wrong username or password") % request.params[
                    'login']
            if not unsuccessful_message or uid is SUPERUSER_ID:
                self.save_session(
                    user.tz,
                    request.httprequest.session.sid)
                return http.redirect_with_hash(redirect)
            user = request.env.user
            self.save_session(
                user.tz,
                request.httprequest.session.sid,
                unsuccessful_message)
            _logger.error(unsuccessful_message)
            request.uid = old_uid
            values['error'] = _('Login failed due to one of the following reasons:')
            values['reason1'] = _('- Wrong login/password')
            values['reason2'] = _('- User not allowed to have multiple logins')
            values[
                'reason3'] = _('- User not allowed to login at this specific time or day')
        return request.render('web.login', values)

    def save_session(
            self,
            tz,
            sid,
            unsuccessful_message='',
            ):
        now = fields.datetime.now()
        session_obj = request.env['ir.sessions']
        cr = request.registry.cursor()

        # Get IP, check if it's behind a proxy
        ip = request.httprequest.headers.environ['REMOTE_ADDR']
        forwarded_for = ''
        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.headers.environ and request.httprequest.headers.environ[
            'HTTP_X_FORWARDED_FOR']:
            forwarded_for = request.httprequest.headers.environ['HTTP_X_FORWARDED_FOR'].split(', ')
            if forwarded_for and forwarded_for[0]:
                ip = forwarded_for[0]

        # for GeoIP
        geo_ip_resolver = None
        ip_location = ''
        try:
            import GeoIP
            geo_ip_resolver = GeoIP.open(
                '/usr/share/GeoIP/GeoIP.dat',
                GeoIP.GEOIP_STANDARD)
        except ImportError:
            geo_ip_resolver = False
        if geo_ip_resolver:
            ip_location = (str(geo_ip_resolver.country_name_by_addr(ip)) or '')

        # autocommit: our single update request will be performed atomically.
        # (In this way, there is no opportunity to have two transactions
        # interleaving their cr.execute()..cr.commit() calls and have one
        # of them rolled back due to a concurrent access.)
        cr.autocommit(True)
        user = request.env.user
        logged_in = True
        uid = user.id
        if unsuccessful_message:
            uid = SUPERUSER_ID
            logged_in = False
            sessions = False
        else:
            sessions = session_obj.search([('session_id', '=', sid),
                                                    ('ip', '=', ip),
                                                    ('user_id', '=', uid),
                                                    ('logged_in', '=', True)],
                                          )
        if not sessions:
            expriy_date = (now + relativedelta(seconds= user.session_default_seconds)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            values = {
                'user_id': uid,
                'logged_in': logged_in,
                'session_id': sid,
                'session_seconds': user.session_default_seconds,
                'multiple_sessions_block': user.multiple_sessions_block,
                'date_login': now.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'expiration_date': expriy_date,
                'ip': ip,
                'ip_location': ip_location,
                'remote_tz': tz or 'GMT',
                'unsuccessful_message': unsuccessful_message,
            }
            session_obj.sudo().create(values)
            cr.commit()
        cr.close()

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True, logout_type='ul')
        return werkzeug.utils.redirect(redirect, 303)
