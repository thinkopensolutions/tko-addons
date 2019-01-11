

from openerp import models

class survey_mail_compose_message(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    # set survey and mail template
    def default_get(self, cr, uid, fields, context=None):
        res = super(survey_mail_compose_message, self).default_get(cr, uid, fields, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        templates = ir_model_data.get_object_reference(cr, uid,
                                                       'survey', 'email_template_survey')
        template_id = templates[1] if len(templates) > 0 else False
        if context.get('active_model') == 'crm.lead' and context.get('active_ids'):
            lead_obj = self.pool.get('crm.lead').browse(cr, uid, context.get('active_id'))
            res.update({'survey_id': lead_obj.stage_id.survey_id and lead_obj.stage_id.survey_id.id or False,
                        'template_id' : lead_obj.stage_id.template_id and lead_obj.stage_id.template_id.id or template_id})
        return res

    # must be defined this method
    # it passes context to create method , we can use that to set lead in user input lines
    def send_mail(self, cr, uid, ids, context=None):
        active_id = context.get('active_id', False)
        if context.get('active_model') == 'crm.lead' and  active_id:
            for wizard in self.browse(cr, uid, ids, context=context):
                self.pool.get('crm.lead').message_post(cr, uid, [active_id], body=wizard.body, subject=wizard.subject, context=context)
        return super(survey_mail_compose_message, self).send_mail(cr, uid, ids, context=context)