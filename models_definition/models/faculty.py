from odoo import models, api, fields, _

class Faculty(models.Model):
    _name = 'faculty'
    _description = "Faculty"
    
    facu_auto = fields.Char(string="Autorización", required=True)
    facu_univ = fields.Char(string="Universidad", required=True)
    facu_codi = fields.Char(string="Código", required=True)
    facu_nomb = fields.Char(string="Nombre", required=True)
    facu_dire = fields.Char(string="Dirección")
    facu_emai = fields.Char(string="Correo")
    facu_url = fields.Char(string="Sitio web")
    facu_obse = fields.Char(string="No sé")
    facu_logo = fields.Image(string='Logo', max_width=500, max_height=500)
    facu_sigl = fields.Char(string="No sé")
    facu_nume = fields.Char(string="Código de control de estudios")
    # facu_crea
    # facu_cusu
    # facu_modi
    # facu_musu
