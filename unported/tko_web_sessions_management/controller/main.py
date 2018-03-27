# -*- encoding: utf-8 -*-

import simplejson

from odoo import http
from odoo.http import request


class websession(http.Controller):
    @http.route(['/ajax/session/'], auth="public", website=True)
    def property_map(self, **kwargs):
        session = []
        if request.session.uid == None:
            session.append({'result': 'true'})
            content = simplejson.dumps(session)
            return request.make_response(content, [('Content-Type', 'application/json;charset=utf-8')])
