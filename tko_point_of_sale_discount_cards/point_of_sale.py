from openerp import fields, models, api, _

class pos_discount_cards(models.Model):
    _name = 'pos.discount.cards'
    
    name = fields.Char('Name', required=True)
    type = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    active = fields.Boolean('Active', default=True)


class pos_config(models.Model):
    _inherit = 'pos.config'
    
    discount_card_ids = fields.Many2many('pos.discount.cards', string='Discount cards')
    
    
class pos_session(models.Model):
    _inherit = 'pos.session'
    
    discount_card_ids = fields.Many2many('pos.discount.cards', 'pos_session_cards_rel', 'session_id', 'card_id', related='config_id.discount_card_ids', readonly=True, string='Available Discount Cards')
