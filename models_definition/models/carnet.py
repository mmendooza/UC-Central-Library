# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Carnet(models.Model):
    _name = "carnet"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Library cards"

    active = fields.Boolean(
        default=True, help="Set active to false to hide the salary advance tag without removing it.")

    # name = fields.Many2one(string='Usuario', comodel_name='internal.user', ondelete='restrict')
    carn_unid = fields.Char(string='Codigo de la unidad operador',
                            help='Codigo de la unidad operador')
    carn_oper = fields.Char(string='Codigo de operador',
                            help='Codigo de operador')
    carn_usua = fields.Char(string='Codigo de usuario prestamo',
                            help='Codigo de usuario prestamo')
    carn_unop = fields.Char(string='Codigo unidad de usuario prestamo',
                            help='Codigo unidad de usuario prestamo')
    carn_tipo = fields.Char(string='Codigo tipo de usuario',
                            help='Codigo tipo de usuario')
    carn_facu = fields.Char(string='Facultad', help='Facultad')
    carn_escu = fields.Char(string='Escuela', help='Escuela')
    carn_menc = fields.Char(string='Especialidad',
                            help='Especialidad')
    carn_anio = fields.Char(string='Año o semestre',
                            help='Año o semestre')
    carn_secc = fields.Char(string='Seccion', help='Seccion')
    carn_venc = fields.Date(string='Fecha de vencimiento',
                            help='Fecha de vencimiento')
    carn_nume = fields.Integer(
        string='Numero de carnet', help='Numero de carnet')
    card_stat = fields.Integer(
        string='Estado del carnet', help='Indica si el carnet esta Activo o no')
    card_moti = fields.Char(string='Descripcion motivo',
                            help='Descripcion motivo')
    card_mont = fields.Char(string='Costo del carnet',
                            help='Costo del carnet')
    card_etiq = fields.Char(string='Etiqueta', help='Etiqueta')
    card_etvi = fields.Boolean(
        string='Etiqueta visible', help='Etiqueta visible o no')
    card_tiqu = fields.Char(string='Numero tique factura',
                            help='Numero tique factura')
    carn_loca = fields.Char(string='Código de lotecarnet',
                            help='Código de lotecarnet')
    carn_crea = fields.Datetime(
        string='Fecha de creación del carnet', help='Fecha de creación del carnet')
    carn_modi = fields.Datetime(string='Fecha de la ultima modificación del carnet',
                                help='Fecha de la ultima modificación del carnet')
    carn_umod = fields.Char(string='Ultimo usuario que modifico',
                            help='Ultimo usuario que modifico')

    # operator = fields.Many2one(string='Operador', comodel_name='', ondelete='restrict', required=True)
    # university_career = fields.Many2one(string='Carrera', comodel_name='', ondelete='restrict', required=True)
    # blocked_card = fields.Boolean(string='Bloqueado')
    # carnet_operator_code = fields.Char(related='operator.code')
    # user_type_code = fields.Char(related='name.code')
    # faculty_card = fields.Char(related='university_career.facultad.name')
    # school_card = fields.Char(related='university_career.escuela.name)
    # mention_card = fields.Char(related='mention.name)
    # card_year = fields.Integer(related='name.current_year')
    # card_type_system = fields.Selection(related='name.type_of_system')
    # card_expiration_date = fields.Date(string='Fecha de vencimiento', required=True)
    # card_number = fields.Integer(string='Número del carnet')
    # card_status = fields.Boolean(string='Estado del carnet', help='Indica si el carnet esta Activo o no', required=True)
    # reason_for_card = fields.Char(string='Descripción del carnet', help='Descripción o motivo del carnet', required=True)
    # cost_the_card = fields.Float(string='Costo del carnet', required=True)
    # card_label = fields.Char(string='Etiqueta')
    # carn_evit = fields.Boolean(string='Visible o Oculta')
    # carn_tiqu = fields.Float(string='Número de tiquet o factura')
    # date_last_card_modification = fields.Date(string='Fecha de la ultima modificación del carnet')
    # date_last_user_to_modify = fields.Date(string='Fecha de la ultima modificación del carnet')
