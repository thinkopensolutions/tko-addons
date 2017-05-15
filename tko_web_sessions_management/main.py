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

import openerp
import werkzeug.contrib.sessions
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

# from openerp import pooler

_logger = logging.getLogger(__name__)


class TkobrSessionMixin(object):

    def check_session(self, db, login, password):
        _logger.debug('Authentication method: TkobrSessionMixin.check_session !')
        multi_ok = True
        calendar_set = 0
        calendar_ok = False
        calendar_group = ''
        unsuccessful_message = ''
        now = datetime.now()

        uid = db and login and password and request.session.authenticate(db, login, password)
        if uid is not False:
            user = request.registry.get('res.users').browse(
                request.cr, request.uid, uid, request.context)
            if not uid is SUPERUSER_ID:
                # check for multiple sessions block
                sessions = request.registry.get('ir.sessions').search(
                    request.cr, request.uid, [
                        ('user_id', '=', uid), ('logged_in', '=', True)], context=request.context)

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
                                                   login
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
                                                           login, group.name)
                                break
                        if calendar_set > 0 and calendar_ok == False:
                            unsuccessful_message = _(
                                "unsuccessful login from '%s', user time out of allowed calendar defined in group '%s'") % (
                                                       login, calendar_group)
                else:
                    unsuccessful_message = _("unsuccessful login from '%s', multisessions block defined in user") % \
                                           login
        else:
            unsuccessful_message = _("unsuccessful login from '%s', wrong username or password") % login
        access_granted = not unsuccessful_message or uid is SUPERUSER_ID
        if access_granted:
            self.save_session(
                request.cr,
                uid,
                user.tz,
                request.httprequest.session.sid,
                context=request.context)
        else:
            user = request.registry.get('res.users').browse(
                request.cr, SUPERUSER_ID, SUPERUSER_ID, request.context)
            self.save_session(
                request.cr,
                uid,
                user.tz,
                request.httprequest.session.sid,
                unsuccessful_message,
                request.context)
            _logger.error(unsuccessful_message)
        return access_granted, uid, unsuccessful_message

    def save_session(
            self,
            cr,
            uid,
            tz,
            sid,
            unsuccessful_message='',
            context=None):
        now = fields.datetime.now()
        session_obj = request.registry.get('ir.sessions')
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
        user = request.registry.get('res.users').browse(
            cr, request.uid, uid, request.context)
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
                'expiration_date': datetime.strftime(
                    (datetime.strptime(
                        now,
                        DEFAULT_SERVER_DATETIME_FORMAT) +
                     relativedelta(
                         seconds=user.session_default_seconds)),
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'ip': ip,
                'ip_location': ip_location,
                'remote_tz': tz or 'GMT',
                'unsuccessful_message': unsuccessful_message,
            }
            session_obj.create(cr, uid, values, context=context)
            cr.commit()
        cr.close()
        return True


class Session_tkobr(openerp.addons.web.controllers.main.Session, TkobrSessionMixin):

    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        _logger.debug('Authentication method: Session_tkobr.authenticate !')
        old_uid = request.uid
        (access_granted, uid, unsuccessful_message) = self.check_session(db, login, password)
        if not access_granted:
            password = None
            request.uid = old_uid
            # TODO: custom fail message
        return super(Session_tkobr, self).authenticate(db, login, password, base_location=base_location)


class Home_tkobr(openerp.addons.web.controllers.main.Home, TkobrSessionMixin):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        if not request.registry.get('ir.sessions'):
            return super(Home_tkobr,self).web_login(redirect=redirect, **kw)
        _logger.debug('Authentication method: Home_tkobr.web_login !')
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
            db = request.session.db
            login = request.params.get('login', None)
            password = request.params.get('password', None)
            (access_granted, uid, unsuccessful_message) = self.check_session(db, login, password)
            if access_granted:
                return http.redirect_with_hash(redirect)
            else:
                request.uid = old_uid
                values['error'] = _('Login failed due to one of the following reasons:')
                values['reason1'] = _('- Wrong login/password')
                values['reason2'] = _('- User not allowed to have multiple logins')
                values[
                    'reason3'] = _('- User not allowed to login at this specific time or day')
        return request.render('web.login', values)


    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True, logout_type='ul')
        return werkzeug.utils.redirect(redirect, 303)
