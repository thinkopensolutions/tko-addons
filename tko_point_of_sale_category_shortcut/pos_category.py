from openerp import fields, models


class pos_category(models.Model):
    _inherit = 'pos.category'

    pos_shortcut = fields.Boolean("Short Cut")
