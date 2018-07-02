# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # set cnpj_cpf and phone on signup
    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        res = super(ResPartner, self).signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        if partner.signup_valid:
            res['cnpj_cpf'] = partner.cnpj_cpf
            res['phone'] = partner.phone
        return res

    # replace http:// and https:// from the link because email templates adds a new http becuase it is a a tag
    # hence it results in dead link https://http//pronova.com.br
    # this is a hack, passking raw link without http or https
    @api.multi
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        raw_base_url = base_url.replace('http://', '').replace('http: //', '').replace('https://', '').replace(
            'https: //', '')
        for partner in self:
            res = super(ResPartner, self)._get_signup_url_for_action(action=action, view_type=view_type,
                                                                     menu_id=menu_id,
                                                                     res_id=res_id, model=model)
            if res[partner.id]:
                res[partner.id] = res[partner.id].replace(base_url, raw_base_url)
        return res
