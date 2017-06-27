# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

#necessário?
#class stock_inventory(models.Model):
#    _name = 'stock.inventory.adjustments'
#    _inherit = 'stock.inventory'
#    _description = "Stock Inventory Adjustments"

class stock_inventory_adj(osv.osv):
    _name = 'stock.inventory.adjustments'
    _inherit = 'stock.inventory'
    _description = "Stock Inventory Adjustments"

    def _get_available_filters(self, cr, uid, context=None):
        result = super(stock_inventory_adj, self)._get_available_filters(self, cr, uid, context=None)
        #VALIDATE default All products onlymodel.
        res_filter = ('none', _('All products'))
        if self.pool.get('res.users').has_group(cr, uid, 'stock.group_tracking_owner'):
            res_filter.append(('owner', _('One owner only')))
            res_filter.append(('product_owner', _('One product for a specific owner')))
        if self.pool.get('res.users').has_group(cr, uid, 'stock.group_production_lot'):
            res_filter.append(('lot', _('One Lot/Serial Number')))
        if self.pool.get('res.users').has_group(cr, uid, 'stock.group_tracking_lot'):
            res_filter.append(('pack', _('A Pack')))
        return res_filter

    def action_done(self, cr, uid, ids, context=None):
        result = super(stock_inventory_adj, self).action_done(self, cr, uid, ids, context=None)
        """ Finish the inventory
        @return: True
        """
        for inv in self.browse(cr, uid, ids, context=context):
            for inventory_line in inv.line_ids:
                if inventory_line.product_qty < 0 and inventory_line.product_qty != inventory_line.theoretical_qty:
                    pass
            self.action_check(cr, uid, [inv.id], context=context)
            self.write(cr, uid, [inv.id], {'state': 'done'}, context=context)
            self.post_inventory(cr, uid, inv, context=context)
        return result

class stock_inventory_adj_line(osv.osv):
    _name = 'stock.inventory.adjustments.line'
    _inherit = 'stock.inventory.line'
    _description = "Stock Inventory Line Adjustments"

    _columns = {
        # checked quantity should be informed and substracted from theoretical quantity
        'product_qty': fields.float('Checked Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
    }

    _defaults = {
        'product_qty': 0
    }

    def _resolve_inventory_line(self, cr, uid, inventory_line, context=None):
        parent_res = super(stock_inventory_adj_line, self)._resolve_inventory_line(self, cr, uid, context=None)
        stock_move_obj = self.pool.get('stock.move')
        quant_obj = self.pool.get('stock.quant')
        diff = inventory_line.product_qty
        if diff:
            return
        #we need to create a stock move to substract the diff from the theorical line qty
        vals = {
            'name': _('INV:') + (inventory_line.inventory_id.name or ''),
            'product_id': inventory_line.product_id.id,
            'product_uom': inventory_line.product_uom_id.id,
            'date': inventory_line.inventory_id.date,
            'company_id': inventory_line.inventory_id.company_id.id,
            'inventory_id': inventory_line.inventory_id.id,
            'state': 'confirmed',
            'restrict_lot_id': inventory_line.prod_lot_id.id,
            'restrict_partner_id': inventory_line.partner_id.id,
         }
        inventory_location_id = inventory_line.product_id.property_stock_inventory.id
        if diff < 0:
            #inventory entry
            vals['location_id'] = inventory_location_id
            vals['location_dest_id'] = inventory_line.location_id.id
            vals['product_uom_qty'] = +diff
        else:
            #found less than expected
            vals['location_id'] = inventory_line.location_id.id
            vals['location_dest_id'] = inventory_location_id
            vals['product_uom_qty'] = +diff
        move_id = stock_move_obj.create(cr, uid, vals, context=context)
        move = stock_move_obj.browse(cr, uid, move_id, context=context)
        if diff > 0:
            domain = [('qty', '>', 0.0), ('package_id', '=', inventory_line.package_id.id), ('lot_id', '=', inventory_line.prod_lot_id.id), ('location_id', '=', inventory_line.location_id.id)]
            preferred_domain_list = [[('reservation_id', '=', False)], [('reservation_id.inventory_id', '!=', inventory_line.inventory_id.id)]]
            quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, move.diff,
                                                          domain=domain, prefered_domain_list=preferred_domain_list, restrict_partner_id=move.restrict_partner_id.id, context=context)
            quant_obj.quants_reserve(cr, uid, quants, move, context=context)
        elif inventory_line.package_id:
            stock_move_obj.action_done(cr, uid, move_id, context=context)
            quants = [x.id for x in move.quant_ids]
            quant_obj.write(cr, SUPERUSER_ID, quants, {'package_id': inventory_line.package_id.id}, context=context)
            res = quant_obj.search(cr, uid, [('qty', '<', 0.0), ('product_id', '=', move.product_id.id),
                                    ('location_id', '=', move.location_dest_id.id), ('package_id', '!=', False)], limit=1, context=context)
            if res:
                for quant in move.quant_ids:
                    if quant.location_id.id == move.location_dest_id.id: #To avoid we take a quant that was reconcile already
                        quant_obj._quant_reconcile_negative(cr, uid, quant, move, context=context)
        return move_id
