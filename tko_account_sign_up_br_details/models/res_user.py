# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
	_inherit = 'res.users'

	@api.model
	def signup(self, values, token=None):
		""" signup a user, to either:
			- create a new user (no token), or
			- create a user for a partner (with token, but no user for partner), or
			- change the password of a user (with token, and existing user).
			:param values: a dictionary with field values that are written on user
			:param token: signup token (optional)
			:return: (dbname, login, password) for the signed up user
		"""
		
		if token:
			partner = self.env['res.partner']._signup_retrieve_partner(token, check_validity=True, raise_exception=True)
			partner_user = partner.user_ids and partner.user_ids[0] or False
			if partner_user:
				values['cnpj_cpf'] = values.get('cnpj_cpf')
				values['company_type'] = values.get('company_type')
		else:
			values['company_type'] = values.get('company_type')
			values['cnpj_cpf'] = values.get('cnpj_cpf')
		return super(ResUsers, self).signup(values, token)