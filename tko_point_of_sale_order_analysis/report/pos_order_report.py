# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp.osv import fields, osv


class report_pos_order_tko(osv.osv):
    _name = "report.pos.order.tko"
    _description = "Point of Sale Orders Statistics"
    _auto = False

    _columns = {
        'date': fields.datetime('Date Order', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'state': fields.selection(
            [('draft', 'New'), ('paid', 'Closed'), ('done', 'Synchronized'), ('invoiced', 'Invoiced'),
             ('cancel', 'Cancelled')],
            'Status'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesperson', readonly=True),
        'location_id': fields.many2one('stock.location', 'Location', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'nbr': fields.integer('# of Lines', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'order_id': fields.many2one('pos.order', 'Order'),
        'total_discount': fields.float('Total Discount', readonly=True),
        'total_liquid': fields.float('Total Liquid', readonly=True),
        'average_price': fields.float('Average Price', readonly=True, group_operator="avg"),
        'order_type': fields.selection([('v', 'Venda'), ('t', 'Troca'), ('c', 'Cancelamento')],
                                       string=u'Internal Reference', readonly=True),

    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order_tko')
        cr.execute("""
            create or replace view report_pos_order_tko as (
                select
                    min(o.id) as id,
                    count(*) as nbr,
                    o.location_id as location_id,
                    o.sale_journal as journal_id,
                    o.order_type as order_type,
                    o.partner_id as partner_id,
                    o.date_order as date,
                    o.user_id as user_id,
                    o.company_id as company_id,
                    o.state as state,
                    (AVG((l.qty * l.price_unit) - ((l.qty * l.price_unit) * (l.discount / 100) + coalesce(o.discount_on_order / o.no_lines ))) ) as average_price,
                    sum((l.qty * l.price_unit) * (l.discount / 100) + (o.discount_on_order / o.no_lines )) as total_discount,
                    sum((l.qty * l.price_unit) - ((l.qty * l.price_unit) * (l.discount / 100) + coalesce(o.discount_on_order / o.no_lines ))) as total_liquid,
                    l.order_id as order_id


                from pos_order as o left join pos_order_line l on (o.id=l.order_id)
                group by
                   o.user_id,o.partner_id,o.company_id,o.location_id,o.sale_journal,o.order_type,o.state,o.date_order,l.order_id
                )""")

        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: