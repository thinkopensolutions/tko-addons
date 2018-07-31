from odoo import api, models, fields
from odoo import tools


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    reason = fields.Char('Reason')
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.uid)


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    reason = fields.Char(string='Reason', related='inventory_id.reason', store=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True, related='inventory_id.user_id',
                              default=lambda self: self.env.uid)
    mode = fields.Selection([('p', ' + '), ('n', ' - ')], compute='get_mode', default='p', required=True, string='Mode')

    @api.one
    @api.depends('product_qty', 'theoretical_qty')
    def get_mode(self):
        if self.product_qty >= self.theoretical_qty:
            self.mode = 'p'
        else: self.mode = 'n'