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
from openerp import api


class res_company(osv.osv):
    _inherit = 'res.company'

    #=========================================================================
    # def _get_partner(self, cr, uid, ids, context=None):
    #     result = {}
    #     for part in self.browse(cr, uid, ids, context=context):
    #         result[part.company_id.id] = True
    #     return result.keys()
    #=========================================================================

    _columns = {
        'email': fields.related(
            'partner_id',
            'email',
            size=64,
            type='char',
            string="Email",
        ),
    }

    def create(self, cr, uid, vals, context=None):
        company_id = super(
            res_company,
            self).create(
            cr,
            uid,
            vals,
            context=context)
        if 'email' in vals.keys() and 'partner_id' in vals.keys() and vals[
                'email'] and vals['partner_id']:
            mail_obj = self.pool.get('res.partner.email')
            mail_obj.create(cr, uid, {'email': vals['email'], 'res_partner_id': vals[
                            'partner_id'], 'is_active': True})

        return company_id
