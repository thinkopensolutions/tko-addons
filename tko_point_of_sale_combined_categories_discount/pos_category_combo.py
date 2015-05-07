from openerp import fields, models, api, _




class pos_category_combo(models.Model):
    _name = 'pos.category.combo'
    
    main_category_id = fields.Many2one('pos.category', 'Main Category', required=True)
    disc_category_id = fields.Many2one('pos.category', 'Discount Category', required=True)
    type = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    
    _sql_constraints = [('category_combo_unique', 'unique(main_category_id, disc_category_id)', _('You already have a combo with current selected categories')),]
    

#adding field becuase we need to have values of combo ids even if no internet connection   

class pos_session(models.Model):
    _inherit = 'pos.session'
    
    combo_ids = fields.Many2many('pos.category.combo','session_combo_rel','session_id', related='config_id.combo_ids', string='Combo Discount')
     

class pos_config(models.Model):
    _inherit = 'pos.config'
    
    combo_ids = fields.Many2many('pos.category.combo','config_combo_rel','config_id', 'combo_id',  compute='get_category_combo_ids', string='Combo Discount')
    
    def get_category_combo_ids(self):
        for records in self:
            combo_ids = self.env['pos.category.combo'].search([])
            records.combo_ids = [(6 , 0 , [combo_id.id for combo_id in combo_ids])]
    
