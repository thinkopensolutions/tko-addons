# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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


class curriculum_department(osv.osv):
    _name = "curriculum.department"
    _description = "curriculum_department model"
    _columns = {
        'name': fields.char('Department', size=64, required=True),
    }

    _order = 'name'


curriculum_department()


class curriculum_job_position(osv.osv):
    _name = "curriculum.job.position"
    _description = "curriculum_job_position model"
    _columns = {
        'name': fields.char('Position', size=64, required=True),
        'depart_id': fields.many2one('curriculum.department', 'Department', required=True)
    }

    _order = 'name'


curriculum_job_position()
