from openerp import fields, models, api, _

class pos_discount_cards(models.Model):
    _name = 'pos.discount.cards'
    
    name = fields.Char('Name', required=True)
    type = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    pos_config_id = fields.Many2one('pos.config', 'POS', required=True)
