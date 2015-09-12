# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from datetime import timedelta , datetime


class issue_to_task(osv.osv_memory):
    _name = 'issue.to.task'
    
    _columns = {
            'name':fields.char('Task Name', required=True),
            'planned_hours': fields.float('Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.', required=True),
            'deadline':fields.datetime('Deadline', required=True)
                    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        values = {} 
        active_id = context.get('active_id', False)
        if active_id:
            active_obj = self.pool.get('project.issue').browse(cr, uid, active_id)
            values['name'] = active_obj.name
        return values
    
    def convert_to_task(self, cr, uid, ids, context=None):
        active_id = context.get('active_id', False)
        if active_id:
            issue_obj = self.pool.get('project.issue').browse(cr, uid, active_id)
            task_obj = self.pool.get('project.task')
            self_obj = self.browse(cr, uid, ids)[0]
            categs = []
            categ_ids = [categs.append(categ.id) for categ in issue_obj.categ_ids]
            vals = {
                    'name' : self_obj.name,
                    'project_id' : issue_obj.project_id.id,
                    'partner_id' : issue_obj.partner_id.id,
                    'description' : issue_obj.description,
                    'version_id' : issue_obj.version_id.id,
                    'priority' : issue_obj.priority,
                    'user_id' : issue_obj.user_id.id,
                    'categ_ids' : [(6, 0, categs)],
                    'planned_hours' : self_obj.planned_hours,
                    'remaining_hours' : self_obj.planned_hours,
                    'date_end' : self_obj.deadline,
                    'issue_id' : active_id,
                    'date_deadline' : datetime.strptime(self_obj.deadline, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
                    }
            
            task_id = task_obj.create(cr, uid, vals , context=context) 
            stage_id = self.pool.get('project.task.type').search(cr, uid, ['|', ('name', '=ilike', 'Done'), ('name', '=ilike', u'Concluído')])
            self.pool.get('project.issue').write(cr, uid, [active_id], {'task_id':task_id, 'stage_id':stage_id and stage_id[0]}, context=None)  
            
            mod_obj = self.pool.get('ir.model.data')
            
            res = mod_obj.get_object_reference(cr, uid, 'project', 'view_task_form2')
            
            return {
                'name': 'Task',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res and res[1] or False],
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'res_id': task_id  or False,  # #please replace record_id and provide the id of the record to be opened  False to open new wizard
            }
            
            
