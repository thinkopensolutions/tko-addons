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

from openerp import models, api, fields
from lxml import etree

dynamic_fields_list = ['field1_test','field2_test','field3_test','field4_test','field5_test']
class task_type(models.Model):
    _name = 'task.type'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index', size=1)
    task_id = fields.Many2one('project.task', string='Task')
    field_ids = fields.Many2many('ir.model.fields','task_type_fields_rel','fields_id','type_id', string='Fields', domain=[('dynamic_view_field','=',True)])


class project_task(models.Model):
    _inherit = 'project.task'

    type_name = fields.Char(
        compute='_get_type_name',
        store=True,
        string='Name')
    task_type_id = fields.Many2one('task.type', string='Type')
    color = fields.Integer(compute='_get_color', string='Color', store=False)
    field1_test = fields.Char('Field1', dynamic_view_field=True)
    field2_test = fields.Char('Field2', dynamic_view_field=True)
    field3_test = fields.Char('Field3', dynamic_view_field=True)
    field4_test = fields.Char('Field4', dynamic_view_field=True)
    field5_test = fields.Char('Field5', dynamic_view_field=True)
    field6_test = fields.Char('Field5', dynamic_view_field=True)
    field7_test = fields.Char('Field5', dynamic_view_field=True)
    field8_test = fields.Char('Field5', dynamic_view_field=True)
    field1_test_show = fields.Boolean(compute='_get_field_show', string='Show Field1')
    field2_test_show = fields.Boolean(compute='_get_field_show', string='Show Field2')
    field3_test_show = fields.Boolean(compute='_get_field_show', string='Show Field3')
    field4_test_show = fields.Boolean(compute='_get_field_show', string='Show Field4')
    field5_test_show = fields.Boolean(compute='_get_field_show', string='Show Field5')
    field6_test_show = fields.Boolean(compute='_get_field_show', string='Show Field6')


    @api.depends('task_type_id','task_type_id.field_ids')
    @api.one
    def _get_field_show(self):
        dynamic_fields_list = ['field1_test','field2_test','field3_test','field4_test','field5_test','field6_test']
        field_names = []
        for field in self.task_type_id.field_ids:
            field_names.append(field.name)
        for field_name in dynamic_fields_list:
            #show the field
            if field_name in field_names:
                field_name += '_show'
                setattr(self,field_name, True)
        return True

    # set dynamic_view_field True in fields
    # # dynamic_view_field is custom property
    # @api.model_cr_context
    # def _field_create(self):
    #     result = super(project_task,self)._field_create()
    #     model_fields = sorted(self._fields.itervalues(), key=lambda field: field.type == 'sparse')
    #     for field in model_fields:
    #         if field._attrs.get('dynamic_view_field'):
    #             field_id = self.env['ir.model.fields'].search([('name','=',field.name)], limit=1)
    #             # can't use write becuase manual fields are not allowed to write
    #             if field_id:
    #                 self._cr.execute("update ir_model_fields set dynamic_view_field='t' where id='%s'"%field_id.id)
    #     return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        context = self.env.context
        result = super(project_task, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            eview = etree.fromstring(result['arch'])
            products = eview.xpath("//field[@name='product_id']")
            for product_id in products:
                product_id.set('domain', "[('type','=','service'),('is_fee','=',False)]")
            result['arch'] = etree.tostring(eview)

        return result


    @api.multi
    def name_get(self):
        result = []
        for task in self:
            task_type = task.task_type_id and task.task_type_id.name or ''
            result.append(
                (task.id, "%s %s" %
                 ('[' + task_type + ']', task.name or ' ')))
        return result

    @api.depends('task_type_id.name')
    def _get_type_name(self):
        for record in self:
            if record.task_type_id:
                record.type_name = record.task_type_id.name

    @api.depends('task_type_id.color')
    def _get_color(self):
        for record in self:

            if record.task_type_id:
                record.color = record.task_type_id.color

    @api.onchange('task_type_id')
    def _change_task_type(self):
        result = {'value': {}}
        if self.task_type_id:
            result['value'].update({
                'color': str(self.task_type_id.color)[-1],
                'type_name': self.task_type_id.name,

            })
        return result
