# -*- coding: utf-8 -*-
from openerp import fields, models

class prisme_postit_day(models.Model):
    _name = 'prisme.postit.day'
    _description = "Postit Day"

    name = fields.Char(string="Day name", required=True, translate=True)
    nbr = fields.Integer('Day number', required=True)
