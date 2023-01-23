# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResUsers(models.Model):
    _inherit = "res.users"

    _sql_constraints = [('code_uniq', 'unique (code)', 'Operator code must be unique!')]

    unit_id = fields.Many2one(comodel_name="information.unit", string="Information Unit")
    code = fields.Char(string="Code", size=8)
    position = fields.Char(string="Position")