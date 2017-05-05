# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    smtp_server_id = fields.One2many('ir.mail_server', 'user_id',
                                     'Email Server')
