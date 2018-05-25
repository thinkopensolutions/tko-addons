# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

import logging
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.exceptions import UserError
from odoo.addons.br_base.tools import fiscal
from odoo import http, _

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

    # Set company_type and cnpj_cpf to partner
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'company_type', 'cnpj_cpf')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    # Validate CPF/CNPJ
    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()
        if qcontext.get("cnpj_cpf") and not qcontext.get("error"):
            if qcontext.get("company_type") == 'person':
                if not fiscal.validate_cpf(qcontext.get("cnpj_cpf")):
                    qcontext["error"] = _("Invalid CPF !")
            else:
                if not fiscal.validate_cnpj(qcontext.get("cnpj_cpf")):
                    qcontext["error"] = _("Invalid CNPJ !")
        if not qcontext.get("error") and qcontext.get("cnpj_cpf"):
            if request.env["res.partner"].sudo().search([("cnpj_cpf", "=", qcontext.get("cnpj_cpf"))]):
                qcontext["error"] = _("Another user is already registered using this CNPJ/CPF.")
        return qcontext
