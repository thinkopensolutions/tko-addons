# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import odoo
from dateutil.relativedelta import *
from odoo import SUPERUSER_ID
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file
from odoo.http import request
from odoo.tools.func import lazy_property
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

#
_logger = logging.getLogger(__name__)


class OpenERPSession(odoo.http.OpenERPSession):
    def logout(self, keep_db=False, logout_type=None, env=None):
        try:
            env = env or request.env
        except:
            pass
        if env and hasattr(
                env,
                'registry') and env.registry.get('ir.sessions'):
            session = env['ir.sessions'].sudo().search(
                [('session_id', '=', self.sid),
                 ('logged_in', '=', True), ])
            if session:
                session._on_session_logout(logout_type)
        return super(OpenERPSession, self).logout(keep_db=keep_db)


class Root_tkobr(odoo.http.Root):
    @lazy_property
    def session_store(self):
        # Setup http sessions
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        return werkzeug.contrib.sessions.FilesystemSessionStore(
            path, session_class=OpenERPSession)


root = Root_tkobr()
odoo.http.root.session_store = root.session_store
