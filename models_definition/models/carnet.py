# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Carnet(models.Model):
    _name = "carnet"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = ''
    _description = "Library cards"

    active = fields.Boolean(default=True, help="Set active to false to hide the salary advance tag without removing it.")

    name = fields.Many2one(string='Usuario', comodel_name='internal.user', ondelete='restric', required=True)
    #operator = fields.Many2one(string='Operador', comodel_name='', ondelete='restric', required=True)
    #university_career = fields.Many2one(string='Carrera', comodel_name='', ondelete='restric', required=True)
    blocked_card = fields.Boolean(string='Bloqueado')
    #carnet_operator_code = fields.Char(related='operator.code')
    #user_type_code = fields.Char(related='name.code')
    #faculty_card = fields.Char(related='university_career.facultad.name')
    #school_card = fields.Char(related='university_career.escuela.name)
    #mention_card = fields.Char(related='mention.name)
    card_year = fields.Integer(related='name.current_year')
    #card_type_system = fields.Selection(related='name.type_of_system')
    card_expiration_date = fields.Date(string='Fecha de vencimiento', required=True)
    card_number = fields.Integer(string='Número del carnet')
    card_status = fields.Boolean(string='Estado del carnet', help='Indica si el carnet esta Activo o no', required=True)
    reason_for_card = fields.Char(string='Descripción del carnet', help='Descripción o motivo del carnet', required=True)
    cost_the_card = fields.Float(string='Costo del carnet', required=True)
    #card_label = fields.Char(string='Etiqueta')
    #carn_evit = fields.Boolean(string='Visible o Oculta')
    #carn_tiqu = fields.Float(string='Número de tiquet o factura')
    carn_loca = fields.Char(string='Código de lote',required=True)
    date_creation_card = fields.Date(string='Fecha de creación del carnet')
    date_last_card_modification = fields.Date(string='Fecha de la ultima modificación del carnet')
    date_last_user_to_modify = fields.Date(string='Fecha de la ultima modificación del carnet')

