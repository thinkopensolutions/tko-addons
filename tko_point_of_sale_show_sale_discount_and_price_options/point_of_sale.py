from openerp import fields, models


class pos_config(models.Model):
    _inherit = 'pos.config'

    allow_disc = fields.Boolean(string=u'Allow Discount')
    allow_price = fields.Boolean(string=u'Allow Pricing')


class pos_session(models.Model):
    _inherit = 'pos.session'

    allow_disc = fields.Boolean(string=u'Allow Discount', related='config_id.allow_disc')
    allow_price = fields.Boolean(string=u'Allow Pricing', related='config_id.allow_price')
