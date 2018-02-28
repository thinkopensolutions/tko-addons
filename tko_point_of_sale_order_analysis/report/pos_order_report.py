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
        'order_id': fields.many2one('pos.order', 'Order'),
        'total_discount': fields.float('Total Discount', readonly=True),
        'total_liquid': fields.float('Total Liquid', readonly=True),
        'average_price': fields.float('Average Price', readonly=True, group_operator="avg"),
        'order_type': fields.selection([('v', 'Venda'), ('t', 'Troca'), ('c', 'Cancelamento')], string=u'Order Type', readonly=True),
        'discount_card_name': fields.char(u'Discount Card'),
        'discount_card_type': fields.selection([('p', 'Percentage'), ('fi', 'Fixed')], string=u'Discount Type'),
        'session_id': fields.many2one('pos.session', 'Session',select=1,domain="[('state', '=', 'opened')]",states={'draft' : [('readonly', False)]},readonly=True),
        'discount_on_order': fields.float('Discount on Order'),
        'statement_id': fields.many2one('account.bank.statement', 'Statement', select=True, required=True, ondelete='restrict'),
        'journal_id': fields.related('statement_id', 'journal_id', type='many2one', relation='account.journal', string=u'Journal', store=True, readonly=True),
        'name': fields.related('account_move', 'id', type='char', relation='account.move', string=u'Move Number', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),
        'total_discount': fields.float('Total Discount', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_qty': fields.integer('Product Quantity', readonly=True),
        'product_categ_id': fields.many2one('product.category', 'Product Category', readonly=True),

    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order_tko')
        cr.execute("""
            create or replace view report_pos_order_tko as (
                select
                    min(o.id) as id,
                    count(*) as nbr,
                    sum(l.qty * u.factor) as product_qty,
                    sum(l.qty * l.price_unit) as price_total,
                    o.location_id as location_id,
                    o.order_type as order_type,
                    o.discount_card_name as discount_card_name,
                    o.discount_card_type as discount_card_type,
                    o.session_id as session_id,
                    o.discount_on_order as discount_on_order,
                    b.statement_id as statement_id,
                    b.journal_id as journal_id,
                    m.name as account_move,
                    l.product_id as product_id,
                    t.categ_id as product_categ_id,
                    o.partner_id as partner_id,
                    o.date_order as date,
                    o.user_id as user_id,
                    o.company_id as company_id,
                    o.state as state,
                    (AVG((l.qty * l.price_unit) - ((l.qty * l.price_unit) * (l.discount / 100) + coalesce(o.discount_on_order / o.no_lines ))) ) as average_price,
                    sum((l.qty * l.price_unit) * (l.discount / 100) + (o.discount_on_order / o.no_lines )) as total_discount,
                    sum((l.qty * l.price_unit) - ((l.qty * l.price_unit) * (l.discount / 100) + coalesce(o.discount_on_order / o.no_lines ))) as total_liquid,
                    l.order_id as order_id
                    
                from pos_order as o
                     left join pos_order_line l on (o.id=l.order_id)
                     left join account_bank_statement_line b on (b.pos_statement_id=o.id)
                     left join account_bank_statement s on (s.id=b.statement_id)
                     left join account_move m on (m.id=o.account_move)
                     left join product_product p on (p.id=l.product_id)
                     left join product_template t on (t.id=p.product_tmpl_id)
                     left join product_uom u on (u.id=t.uom_id)
                
                group by
                   o.user_id,o.partner_id,o.company_id,o.location_id,o.order_type,o.discount_card_name,discount_card_type,
                   o.session_id,o.discount_on_order,b.statement_id,b.journal_id,m.name,l.product_id,t.categ_id,
                   o.state,o.date_order,l.order_id
                having
                    sum(l.qty * u.factor) != 0)""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
