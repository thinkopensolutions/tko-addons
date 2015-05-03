from openerp import fields, models, api, _

class pos_discount_cards(models.Model):
    _name = 'pos.discount.cards'
    
    name = fields.Char('Name', required=True)
    type = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    pos_config_id = fields.Many2one('pos.config', 'POS', required=True)
    active = fields.Boolean('Active', default = True)



class pos_config(models.Model):
    _inherit = 'pos.config'
    
    
    pos_discount_card_ids = fields.One2many('pos.discount.cards', 'pos_config_id', 'Discount cards')
    
class pos_session(models.Model):
    _inherit = 'pos.session'
    
    
    pos_discount_card_ids = fields.One2many('pos.discount.cards', realated='config_id.pos_discount_card_ids', readonly=True, string='Available Discount Cards'),
