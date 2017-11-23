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

from openerp.osv import osv, fields


class res_partner_phone(osv.osv):
    _name = "res.partner.phone"
    _description = "partner phone numbers"
    _rec_name = "phone"
    _columns = {
        'phone': fields.char(
            'Number',
            size=64,
            required=True),
        'res_partner_id': fields.many2one(
            'res.partner',
            'Partner ID',
            ondelete="cascade"),
        'type_id': fields.many2one(
            'res.partner.phone.type',
            'Type',
            required=True),
        'is_active': fields.boolean('Is Active'),
    }

    _order = 'phone'

    _defaults = {

        'is_active': False
    }
    _sql_constraints = [
        ('unique_phone_no',
         'unique(phone)',
         "Phone number should be unique !"),
    ]
    _constraints = []

    def set_partner_phone(self, cr, uid, ids, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            phone_ids = self.search(
                cr, uid, [
                    ('res_partner_id', '=', record.res_partner_id.id), ('type_id', '=', record.type_id.id)])
            self.write(cr, uid, phone_ids, {'is_active': False})
            self.write(cr, uid, ids, {'is_active': 't'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class res_partner_phone_type(osv.osv):
    _name = "res.partner.phone.type"
    _description = "Phone type"
    _columns = {
        'name': fields.char('Type', size=64, required=True),
        'code': fields.char('Code', size=64, required=True, readonly=True),
    }
