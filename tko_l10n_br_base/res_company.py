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

from openerp.osv import fields, osv
from res_partner import AVAILABLE_ZONES

class res_company(osv.osv):
    _inherit = 'res.company'
    
    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        return super(res_company, self)._get_address_data(cr, uid, ids, field_names, arg, context=context)
    
    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        return super(res_company, self)._set_address_data(cr, uid, company_id, name, value, arg, context=context)

    _columns = {
        'zone': fields.function(_get_address_data, fnct_inv=_set_address_data, type='selection', selection=AVAILABLE_ZONES, string="Zona", multi='address'),
    }
