from odoo import models, api, fields, _

class School(models.Model):
    _name = 'school'
    _description = "School"

    escu_auto = fields.Char(string="No sé")
    escu_codi = fields.Char(string="Código", required=True)
    escu_facu = fields.Many2one('faculty',string="Facultad")
    escu_nomb = fields.Char(string="Nombre")
    escu_nume = fields.Char(string="Código de control de estudio")
    escu_dire = fields.Char(string="Dirección")
    escu_emai = fields.Char(string="Correo")
    escu_url = fields.Char(string="Sitio web")
    escu_cnu = fields.Char(string="No sé")
    escu_obse = fields.Char(string="No sé")
    escu_logo = fields.Image(string='Logo', max_width=500, max_height=500)
    escu_sigl = fields.Char(string="No sé")
    # escu_crea 
    # escu_cusu
    # escu_modi
    # escu_musu