# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class InformationUnit(models.Model):
    
	_name = "information.unit"
	_description = "Libraries, information centers, documentation centers, archives are information units where users \
    can access information services."

	name = fields.Char(string='Name')