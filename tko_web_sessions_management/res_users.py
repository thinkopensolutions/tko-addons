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
from openerp.http import request


class res_users(osv.osv):
    _inherit = 'res.users'
    
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
#         user_obj = request.registry.get('res.users')
        for id in ids:
            user = self.browse(cr, uid, id, context=context)
            if user.interval_number and user.interval_type:
                u_seconds = (now + _intervalTypes[user.interval_type](user.interval_number) - now).total_seconds()
                if u_seconds < seconds:
                    seconds = u_seconds
            else:
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
            help='The user will be only allowed to login in the calendar defined here.'),
        'multiple_sessions_block': fields.boolean('Block Multiple Sessions', company_dependent=True,
            help='Select this if user can start more than one session'),
        'interval_number': fields.integer('Default Session Duration', company_dependent=True),
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
    
    