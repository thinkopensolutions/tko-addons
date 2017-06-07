from openerp import fields, models, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    department_id = fields.Many2one(
        'curriculum.department', string='Department')
    function_id = fields.Many2one('curriculum.job.position', string='Function')

    @api.onchange('function_id')
    def onchange_function(self):
        if self.function_id:
            self.function = self.function_id.name
        else:
            self.function = False

    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id:
            self.departamento = self.department_id.name
        else:
            self.departamento = False
