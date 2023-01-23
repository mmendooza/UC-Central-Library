# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class InformationUnit(models.Model):
    
	_name = "information.unit"
	_description = "Libraries, information centers, documentation centers, archives are information units where users \
    can access information services."

	_sql_constraints = [('code_uniq', 'unique (code)', 'Unit code must be unique!')]

	name = fields.Char(string='Name')
	code = fields.Char(string="Code")
	faculty_id = fields.Many2one(comodel_name="faculty", string="Faculty", ondelete="restrict")
	library_name = fields.Char(string="Library name")
	address = fields.Char(string="Address")
	website = fields.Char(string="Website Link")
	email = fields.Char(string="Email")
	initials = fields.Char(string="Initials")
