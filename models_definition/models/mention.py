from odoo import models, api, fields, _

class Mention(models.Model):
    _name = 'mention'
    _description = "Mention"
    _rec_name = "menc_nomb"

    menc_nomb = fields.Char(string="Nombre", required=True)
    menc_escu = fields.Many2one(comodel_name="school",string="Escuela", required=True)
    menc_codi = fields.Char(string="Código", required=True)
    menc_nume = fields.Char(string="Número")
    menc_obse = fields.Char(string="No sé menc_obse")
    active = fields.Boolean(default=True)
