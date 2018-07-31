from odoo import api, models, fields, _
from odoo import tools


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    old_quantity = fields.Float('Old Qty', readonly=True)
    update_quantity = fields.Float('Update Qty')
    mode = fields.Selection([('p', ' + '), ('n', ' - ')], default='p', required=True, string='Mode')
    reason = fields.Text('Reason')

    # When a user updates stock qty on the product form, propose the
    # right location to update stock.
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        product_id = res.get('product_id')
        if product_id:
            res.update({'old_quantity': self.env['product.product'].browse(product_id).qty_available})

        return res

    @api.onchange('mode', 'update_quantity')
    def onchange_mode(self):
        if 'new_quantity' not in self._context.keys():
            if self.mode == 'p':
                self.new_quantity = self.old_quantity + self.update_quantity
            else:
                self.new_quantity = self.old_quantity - self.update_quantity

    @api.onchange('new_quantity')
    def onchange_new_quantity(self):
        if self.new_quantity >= self.old_quantity:
            self.mode = 'p'
            self.update_quantity = self.new_quantity - self.old_quantity
        else:
            self.mode = 'n'
            self.update_quantity = self.new_quantity + self.old_quantity

    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']
        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            line_data = wizard._action_start_line()

            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.display_name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'line_ids': [(0, 0, line_data)],
                'reason': self.reason,
            })
            inventory.action_done()
        return {'type': 'ir.actions.act_window_close'}
