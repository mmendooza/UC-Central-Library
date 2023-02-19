from odoo import models, api, fields, _

class Faculty(models.Model):
    _name = 'faculty'
    _description = "Faculty"
    _rec_name = 'facu_nomb'

    facu_nomb = fields.Char(string="Nombre", required=True)
    facu_dire = fields.Char(string="Dirección")
    facu_auto = fields.Char(string="Autorización", required=True)
    facu_univ = fields.Char(string="Universidad", required=True)
    facu_codi = fields.Char(string="Código", required=True)
    facu_nume = fields.Char(string="Código de control de estudios")
    facu_emai = fields.Char(string="Correo")
    facu_url = fields.Char(string="Sitio web")
    facu_obse = fields.Char(string="No sé facu_obse")
    facu_logo = fields.Image(string='Logo', max_width=500, max_height=500)
    facu_sigl = fields.Char(string="No sé facu_sigl")
    active = fields.Boolean(default=True)


