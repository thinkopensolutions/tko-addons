# -*- coding: utf-8 -*-
from openerp import fields, models


class prisme_postit_tag(models.Model):
    _name = 'prisme.postit.tag'
    _description = "Postit Tag"
    name = fields.Char(string="Tag name", required=True)
