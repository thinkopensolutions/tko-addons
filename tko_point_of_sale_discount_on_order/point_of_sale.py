from openerp.osv import osv, fields
import logging
_logger = logging.getLogger(__name__)

import openerp.addons.decimal_precision as dp

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_paid': 0.0,
                'amount_return': 0.0,
                'amount_tax': 0.0,
            }
            val1 = val2 = 0.0
            cur = order.pricelist_id.currency_id
            for payment in order.statement_ids:
                res[order.id]['amount_paid'] += payment.amount
                res[order.id][
                    'amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.lines:
                val1 += line.price_subtotal_incl
                val2 += line.price_subtotal
            res[order.id]['amount_tax'] = cur_obj.round(
                cr, uid, cur, val1 - val2)
            res[order.id]['amount_total'] = cur_obj.round(
                cr, uid, cur, val1 - order.discount_on_order)
        return res

    _columns = {
        'discount_on_order': fields.float('Discount on Order'),
        'amount_tax': fields.function(
            _amount_all,
            string='Taxes',
            digits_compute=dp.get_precision('Account'),
            multi='all'),
        'amount_total': fields.function(
            _amount_all,
            string='Total',
            digits_compute=dp.get_precision('Account'),
            multi='all'),
        'amount_paid': fields.function(
            _amount_all,
            string='Paid',
            states={
                'draft': [
                    ('readonly',
                     False)]},
            readonly=True,
            digits_compute=dp.get_precision('Account'),
            multi='all'),
        'amount_return': fields.function(
            _amount_all,
            'Returned',
            digits_compute=dp.get_precision('Account'),
            multi='all'),
    }

    # pass value of discount_on_order to invoice from POS order
    def action_invoice(self, cr, uid, ids, context=None):
        res = super(
            pos_order,
            self).action_invoice(
            cr,
            uid,
            ids,
            context=context)
        res_id = res.get('res_id', False)
        if res_id:
            for order in self.pool.get('pos.order').browse(
                    cr, uid, ids, context=context):
                self.pool.get('account.invoice').write(cr, uid, [res_id], {
                    'discount_on_order': order.discount_on_order})
        return res
    
    def refund(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            result = super(pos_order,self).refund(cr, uid, [record.id], context=context)
            refuned_id = result.get('res_id',False)
            if refuned_id:
                self.pool.get('pos.order').write(cr, uid, [refuned_id],{'discount_on_order' : -1 * record.discount_on_order})
        
            return result
