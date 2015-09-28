from openerp import models


class res_partner(models.Model):
    _inherit = 'res.partner'

    def action_take_picture(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        res_model, res_id = self.pool.get(
            'ir.model.data').get_object_reference(cr, uid,
                                                  'tko_partner_webcam',
                                                  'action_take_photo')
        dict_act_window = self.pool.get(
            'ir.actions.client').read(cr, uid, res_id, [])
        if not dict_act_window.get('params', False):
            dict_act_window.update({'params': {}})
        dict_act_window['params'].update(
            {'partner_id': len(ids) and ids[0] or False})
        return dict_act_window
