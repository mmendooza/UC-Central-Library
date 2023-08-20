# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InternalUser(models.Model):
	_name = "internal.user"
	_description = "Usuario interno"

	name = fields.Char(string='Nombre completo', required=True, index=True)
	user_type = fields.Selection([
		('student', 'Estudiante'),
		('professor', 'Docente'),
		('administrative', 'Personal administrativo'),
		('laborer', 'Personal obrero')],
		string='Tipo de usuario',
		required=True
	)
	identification = fields.Char(string='Cédula de identidad', required=True)
	active = fields.Boolean(default=True)
	email = fields.Char(string='Correo electrónico', required=True)
	password = fields.Char(string='Contraseña', required=True)
	phone = fields.Char(string='Teléfono')
	user_address = fields.Char(string='Dirección de habitación', required=True)
	work_address = fields.Char(string='Dirección de trabajo')
	nacionality = fields.Char(string='Nacionalidad', required=True)
	gender = fields.Selection([('M', 'Masculino'), ('F', 'Femenino')], string='Género', required=True)
	current_year = fields.Integer(string='Año/Semestre en curso', required=True)
	birthday = fields.Date(string='Fecha de nacimiento', required=True)
	civil_status = fields.Selection([
		('single', 'Soltero(a)'),
		('married', 'Casado(a)'),
		('divorced', 'Divorciado(a)'),
		('widowed', 'Viudo(a)')],
		string='Estado civil',
		default='single',
		required=True
	)
	disability = fields.Selection([
		('none', 'Ninguna'),
		('hearing', 'Auditiva'),
		('lenguage', 'De lenguaje'),
		('physical', 'Fisica'),
		('intellectual', 'Intelectual'),
		('motor', 'Motriz'),
		('multiple', 'Multiple'),
		('visual', 'Visual')],
		string='Discapacidad',
		default='none',
		required=True
	)
	picture = fields.Image(string='Fotografía', max_width=500, max_height=500, required=True)
	student_certificate = fields.Binary(string='Constancia de estudio')
	worker_certificate = fields.Binary(string='Constancia de trabajo')
	observations = fields.Text(string='Observaciones')
	# sabi_user_id = fields.One2many(comodel_name='sabi.user', inverse_field_name='internal_user_id', string='User Tracking')