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

import re

from openerp.osv import osv, fields


class res_partner_email(osv.osv):
    _name = "res.partner.email"
    _description = "partner email ids"
    _rec_name = 'email'
    _columns = {
        'email': fields.char(
            'Emails', size=240, required=True), 'res_partner_id': fields.many2one(
            'res.partner', 'Partner ID', ondelete="cascade"), 'is_active': fields.boolean(
            string='Active')}

    _sql_constraints = [
        ('unique_email',
         'unique(email)',
         u"e-mail deve ser único!"),
    ]

    _defaults = {
        'is_active': False,
    }

    _order = 'email'

    def _ValidateEmail(self, cr, uid, ids, context=None):
        email = str(self.browse(cr, uid, ids[0], context=context).email)
        if re.match(
                "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                email) != None:
            return True
        return False

    _constraints = (
                       _ValidateEmail,
                       'Error!\nPlease enter a valid email address.',
                       ['email']),

    def set_partner_email(self, cr, uid, ids, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            email_ids = self.search(
                cr, uid, [
                    ('res_partner_id', '=', record.res_partner_id.id)])
            self.write(cr, uid, email_ids, {'is_active': False})
            self.write(cr, uid, ids, {'is_active': 't'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
