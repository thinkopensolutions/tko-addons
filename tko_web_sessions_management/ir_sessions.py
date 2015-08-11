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
from datetime import date, datetime, time, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.http import Response
from openerp import http
from openerp.tools.translate import _
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file

_logger = logging.getLogger(__name__)

LOGOUT_TYPES = [('ul', 'User Logout'),
                ('to', 'Session Timeout'),
                ('sk', 'Session Killed'),]

class ir_sessions(osv.osv):
    _name = 'ir.sessions'
    _description = "Sessions"
    
    _columns = {
        'user_id' : fields.many2one('res.users', 'User', ondelete='cascade',
            required=True),
        'logged_in': fields.boolean('Logged in', required=True, index=True),
        'session_id' : fields.char('Session ID', size=100, required=True),
        'session_seconds': fields.integer('Session duration in seconds'),
        'multiple_sessions_block': fields.boolean('Block Multiple Sessions'),
        'date_login': fields.datetime('Login', required=True),
        'expiration_date': fields.datetime('Expiration Date', required=True,
            index=True),
        'date_logout': fields.datetime('Logout'),
        'logout_type': fields.selection(LOGOUT_TYPES, 'Logout Type'),
        'session_duration': fields.char('Session Duration', size=8),
        'user_kill_id' : fields.many2one('res.users', 'Killer User',),
        # Add other fields about the sessions from HEADER 
        # like Source IPs etc...
        }
    
    _order = 'date_logout desc'
    
    # scheduler function to validate users session
    def validate_sessions(self, cr, uid, context=None):
        ids = self.search(cr, SUPERUSER_ID,
            [('expiration_date', '<=', fields.datetime.now()),
             ('logged_in', '=', True)])
        if ids:
            self.action_close_session(cr, uid, ids, 'to', context)
        return True
    
    def action_close_session(self, cr, uid, ids, logout_type='sk', context=None):
        logout = False
        session_obj = self.pool['ir.sessions']
        sessions = session_obj.read(cr, uid, ids,
            ['date_login', 'session_id'],
            context=context)
        for session in sessions:
            now = fields.datetime.now()
            session_obj.write(cr, uid, session['id'],
                {'logged_in': False,
                 'date_logout': datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT),
                 'logout_type': logout_type,
                 'user_kill_id': uid,
                 'expiration_date': now,
                 'session_duration': str(datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(session['date_login'], DEFAULT_SERVER_DATETIME_FORMAT)),
#                 'session_seconds': -1,
                 },
                context=context)
        return True
    
    