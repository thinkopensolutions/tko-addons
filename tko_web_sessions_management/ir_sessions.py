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
from openerp import api
from openerp.osv import fields, osv, orm
from datetime import date, datetime, time, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.http import Response
from openerp.http import root
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
        'user_kill_id' : fields.many2one('res.users', 'Killed by',),
        'unsuccessful_message' : fields.char('Unsuccessful', size=252),
        'ip': fields.char('Remote IP', size=15),
        'ip_location': fields.char('IP Location',),
        'remote_tz' : fields.char('Remote Time Zone', size=32, required=True),
        # Add other fields about the sessions from HEADER...
        }
    
    _order = 'logged_in desc, expiration_date desc'
    
    # scheduler function to validate users session
    def validate_sessions(self, cr, uid, context=None):
        ids = self.search(cr, SUPERUSER_ID,
            [('expiration_date', '<=', fields.datetime.now()),
             ('logged_in', '=', True)])
        if ids:
            self.browse(cr, SUPERUSER_ID, ids)._close_session(logout_type='to')
        return True
    
    @api.multi
    def action_close_session(self):
        redirect = self._close_session(logout_type='sk')
        if redirect:
            return werkzeug.utils.redirect('/web/login?db=%s' % self.env.cr.dbname, 303)
    
    @api.multi
    def _on_session_logout(self, logout_type=None):
        now = fields.datetime.now()
        session_obj = self.pool['ir.sessions']
        cr = self.pool.cursor()
        # autocommit: our single update request will be performed atomically.
        # (In this way, there is no opportunity to have two transactions
        # interleaving their cr.execute()..cr.commit() calls and have one
        # of them rolled back due to a concurrent access.)
        cr.autocommit(True)
        for r in self:
            session_obj.write(cr, SUPERUSER_ID, r.id,
                    {'logged_in': False,
                     'date_logout': now,
                     'logout_type': logout_type,
                     'user_kill_id': SUPERUSER_ID,
                     'session_duration': str(datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(r.date_login, DEFAULT_SERVER_DATETIME_FORMAT)),
                     })
        cr.commit()
        cr.close()
        return True
        
    @api.multi
    def _close_session(self, logout_type=None):
        redirect = False
        for r in self:
            if r.user_id.id == self.env.user.id:
                redirect = True
            session = root.session_store.get(r.session_id)
            session.logout(logout_type=logout_type, env=self.env)
        return redirect
        
