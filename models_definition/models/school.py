from odoo import models, api, fields, _

class School(models.Model):
    _name = 'school'
    _description = "School"
    _rec_name = 'escu_nomb'

    escu_nomb = fields.Char(string="Nombre", required=True)
    escu_dire = fields.Char(string="Dirección")
    escu_codi = fields.Char(string="Código", required=True)
    escu_facu = fields.Many2one(comodel_name="faculty",string="Facultad", required=True)
    escu_nume = fields.Char(string="Código de control de estudio", required=False)
    escu_auto = fields.Char(string="No sé escu_auto")
    escu_emai = fields.Char(string="Correo")
    escu_url = fields.Char(string="Sitio web")
    escu_cnu = fields.Char(string="No sé escu_cnu")
    escu_obse = fields.Char(string="No sé escu_obse")
    escu_logo = fields.Image(string='Logo', max_width=500, max_height=500)
    escu_sigl = fields.Char(string="No sé escu_sigl")
    active = fields.Boolean(default=True)
