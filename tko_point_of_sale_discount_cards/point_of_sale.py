from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)
_card_type = [('p', 'Percentage'), ('fi', 'Fixed')]
class pos_discount_cards(models.Model):
    _name = 'pos.discount.cards'
    
    name = fields.Char('Name', required=True)
    type = fields.Selection(_card_type, string='Type', required=True)
    value = fields.Float('Value', required=True)
    active = fields.Boolean('Active', default=True)


class pos_config(models.Model):
    _inherit = 'pos.config'
    
    discount_card_ids = fields.Many2many('pos.discount.cards', string='Discount cards')
    
    
class pos_session(models.Model):
    _inherit = 'pos.session'
    
    discount_card_ids = fields.Many2many('pos.discount.cards', 'pos_session_cards_rel', 'session_id', 'card_id', related='config_id.discount_card_ids', readonly=True, string='Available Discount Cards')


class pos_order(models.Model):
    _inherit = 'pos.order'
    
    discount_card_id = fields.Many2one('pos.discount.cards' , string='Discount Cards')
    discount_card_name = fields.Char('Discount Card')
    discount_card_type = fields.Selection(_card_type, string='Type')
    discount_card_value = fields.Char('Card Value')
    
    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        
        
        pos_obj = self.pool.get('pos.order')
        pos_line_object = self.pool.get('pos.order.line')
        table_reserved_obj = self.pool.get("table.reserverd")
        session_obj = self.pool.get('pos.session')
        shop_obj = self.pool.get('sale.shop')
        card_obj = self.pool.get('pos.discount.cards')
        order_ids = super(pos_order,self).create_from_ui(cr, uid, orders, context = context)
        #write discount_card_id to order
        if len(order_ids) == len(orders):
            i = 0
            for tmp_order in orders:
                if 'data' in tmp_order.keys():
                    discount_card_id = tmp_order['data'].get('discount_card_id',False)
                    if discount_card_id:
                        card = card_obj.browse(cr, uid, int(discount_card_id))
                        discount_value = card.value
                        if card.type == 'p':
                            #get total from record
                            total = pos_obj.browse(cr, uid, order_ids[i]).amount_total
                            discount_value = ( total* card.value) / 100
                        
                        pos_obj.write(cr, uid, [order_ids[i]],{
                                                               'discount_card_id' : discount_card_id,
                                                               'discount_card_name': card.name,
                                                               'discount_card_type' : card.type,
                                                               'discount_card_value' : card.value,
                                                                'discount_on_order' : discount_value,
                                                                })
                    if pos_obj.test_paid(cr, uid, [order_ids[i]]):
                        pos_obj.signal_workflow(cr, uid, [order_ids[i]], 'paid')
                    i = i + 1
        return order_ids
        
class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    
    line_subototal = fields.Float(string='Subtotal', compute='_get_line_subtotal',store=True)
    
    
    @api.one
    @api.depends('price_unit','discount','qty')
    def _get_line_subtotal(self):
        self.line_subototal = self.price_unit * (1 - (self.discount or 0.0) / 100.0) * self.qty
