# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class CRMSettings(models.TransientModel):
    _name = 'contact.config.settings'
    _inherit = 'res.config.settings'

    module_tko_partner_multiple_phones = fields.Boolean("Manage Multiple Phones ?",
                                                        help="Manage multiple partner phones")
    module_tko_partner_multiple_emails = fields.Boolean("Manage Multiple Emails ?",
                                                        help="Manage multiple partner Emails")
    module_tko_partner_multiple_adresses = fields.Boolean("Manage Multiple Addresses ?",
                                                          help="Manage multiple partner Addresses")
    module_tko_partner_multiple_assets = fields.Boolean("Manage Multiple Assets ?",
                                                          help="Manage multiple partner Addresses")
    #
    # @api.multi
    # def execute(self):
    #     to_install = list(self.modules_to_install())
    #     _logger.info('Selecting addons %s to install', to_install)
    #
    #     IrModule = self.env['ir.module.module']
    #     modules = []
    #     for name in to_install:
    #         module = IrModule.search([('name', '=', name)], limit=1)
    #         modules.append((name, module))
