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

import openerp
from openerp.osv import fields, osv, orm
from datetime import date, datetime, time, timedelta
from openerp.addons.base.ir.ir_cron import _intervalTypes
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import *
from openerp import models
from openerp import http
from openerp.http import root
from openerp.http import request


class res_users(osv.osv):
    _inherit = 'res.users'
        
    def _check_session_validity(self, db, uid, passwd):
        if not request:
            return
        now = fields.datetime.now()
        session = request.session
        session_store = root.session_store
        
        if session.db and session.uid:
            session_obj = request.registry.get('ir.sessions')
            cr = self.pool.cursor()
            # autocommit: our single update request will be performed atomically.
            # (In this way, there is no opportunity to have two transactions
            # interleaving their cr.execute()..cr.commit() calls and have one
            # of them rolled back due to a concurrent access.)
            cr.autocommit(True)
            session_ids = session_obj.search(cr, uid,
                [('session_id', '=', session.sid),
                 ('expiration_date', '>', now),
                 ('logged_in', '=', True)],
                order='expiration_date asc',
                context=request.context)
            if session_ids:
                if request.httprequest.path[:5] == '/web/':
                    open_sessions = session_obj.read(cr, uid,
                        session_ids, ['logged_in',
                                      'date_login',
                                      'session_seconds',
                                      'expiration_date'],
                        context=request.context)
                    for s in open_sessions:
                        seconds = s['session_seconds']
                        session_obj.write(cr, uid, s['id'],
                            {'expiration_date': datetime.strftime((datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(seconds=seconds)), DEFAULT_SERVER_DATETIME_FORMAT),
                             'session_duration': str(datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(s['date_login'], DEFAULT_SERVER_DATETIME_FORMAT)),},
                            context=request.context)
                    cr.commit()
            else:
                session.logout(logout_type='to', keep_db=True)
            cr.close()
        return True
    
    def check(self, db, uid, passwd):
        res = super(res_users, self).check(db, uid, passwd)
        self._check_session_validity(db, uid, passwd)
        return res
    
    def _get_groups(self, cr, uid, ids, context=None):
        result = set()
        objs = self.pool['res.groups']
        for obj in objs.browse(cr, uid, ids, context=context):
            for user in obj.users:
                result.add(user.id)
        return list(result)
    
    def _get_session_default_seconds(self, cr, uid, ids, name, arg={}, context={}):
        result = {}
        now = datetime.now()
        seconds = (now + _intervalTypes['weeks'](1) - now).total_seconds()
        for id in ids:
            user = self.browse(cr, uid, id, context=context)
            if user.interval_number and user.interval_type:
                u_seconds = (now + _intervalTypes[user.interval_type](user.interval_number) - now).total_seconds()
                if u_seconds < seconds:
                    seconds = u_seconds
            else:
                # Get lowest session time
                for group in user.groups_id:
                    if group.interval_number and group.interval_type:
                        g_seconds = (now + _intervalTypes[group.interval_type](group.interval_number) - now).total_seconds()
                        if g_seconds < seconds:
                            seconds = g_seconds
            result[user.id] = seconds
        return result
    
    _columns = {
        'login_calendar_id': fields.many2one('resource.calendar',
            'Allowed Login Calendar', company_dependent=True,
            help='The user will be only allowed to login in the calendar defined here.\nNOTE:The calendar defined here will overlap all defined in groups.'),
        'multiple_sessions_block': fields.boolean('Block Multiple Sessions', company_dependent=True,
            help='Select this to prevent user to start more than one session.'),
        'interval_number': fields.integer('Default Session Duration', company_dependent=True,
            help='This is the timeout for this user.\nNOTE: The timeout defined here will overlap all the timeouts defined in groups.'),
        'interval_type': fields.selection([('minutes', 'Minutes'),
            ('hours', 'Hours'), ('work_days', 'Work Days'),
            ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
            'Interval Unit', company_dependent=True),
        'session_default_seconds': fields.function(_get_session_default_seconds,
            method=True, string='Session Seconds', type='integer',
            store={
                   'res.users': (
                        lambda self, cr, uid, ids, c={}: ids,
                        ['interval_number', 'interval_type'],
                        10),
                   'res.groups': (_get_groups,
                        ['interval_number', 'interval_type'],
                        10),
                   }),
        'session_ids': fields.one2many('ir.sessions', 'user_id', 'User Sessions')
        }
    
    _defaults = {'multiple_sessions_block': False}
    