from openerp import fields, models, api, _
from datetime import timedelta , datetime

_stage_type = [('i','Initial'),('f','Final'),('c','Cancel')]

class project_task(models.Model):
    _inherit = 'project.task'
    
    date_initiated = fields.Boolean('Task Initiated')
    
    #can't carete on_change because it method doesn't gets triggered with widget="statusbar"
    @api.multi
    def write(self, vals):
        for record in self:
            res = super(project_task,self).write(vals)
            if 'stage_id' in vals:
                if record.stage_id.stage_type == 'i' and not record.date_initiated:
                    vals.update({'date_start' : fields.datetime.now(), 'date_initiated' : True})
                elif record.stage_id.stage_type == 'f' or record.stage_id.stage_type == 'c':
                    vals.update({'date_end' : fields.datetime.now()})
                res = super(project_task,self).write(vals)
        return res
        
        
   
    #not working correctly , added 1 extra day to get correct date
    @api.onchange('date_deadline')
    def onchange_date_deadline(self):
        for record in self:
            if record.date_deadline:
                deadline = datetime.strptime(record.date_deadline,'%Y-%m-%d') + timedelta(days=1)
                record.date_end = deadline
               
class project_task_type(models.Model):
    _inherit = 'project.task.type'
    
    stage_type = fields.Selection(_stage_type, string = 'Type')
    
    
                
