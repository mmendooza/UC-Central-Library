from odoo import models, api, fields, _

class Mention(models.Model):
    _name = 'mention'
    _description = "Mention"

    menc_escu = fields.Many2one('school',string="Escuela", required=True)
    menc_codi = fields.Char(string="Código", required=True)
    menc_nomb = fields.Char(string="Nombre", required=True)
    menc_obse = fields.Char(string="No sé")
    menc_nume = fields.Char(string="Número")
    # menc_crea
    # menc_cusu
    # menc_modi
    # menc_musu