# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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


class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'type': fields.selection([('url', 'URL'), ('binary', 'Binary'), ],
                                 'Type', help="Binary File or URL", required=True, change_default=True),
    }

    # this method will srync attachments between attachment tab and attachment button on top
    def create(self, cr, uid, vals, context=None):
        if 'res_model' in vals:
            if vals['res_model'] == 'res.partner':
                vals.update({'partner_id': vals['res_id']})
        if 'partner_id' in vals and vals['partner_id'] != False:
            vals.update({'res_model': 'res.partner', 'res_id': vals['partner_id']})
        return super(ir_attachment, self).create(cr, uid, vals, context=context)


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'attachment_ids': fields.one2many('ir.attachment', 'partner_id', 'Attachments')
    }
