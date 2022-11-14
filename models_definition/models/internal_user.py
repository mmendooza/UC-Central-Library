# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InternalUser(models.Model):
	_name = "internal.user"
	_description = "Usuario interno"

	name = fields.Char(string='Nombre completo', required=True, index=True)
	user_type = fields.Selection([
		('student', 'Alumno'),
		('professor', 'Docente'),
		('administrative', 'Personal administrativo'),
		('laborer', 'Personal obrero')],
		string='Tipo de usuario',
		required=True
	)
	identification = fields.Char(string='Cedula de identidad', required=True)
	active = fields.Boolean(string='¿Activo?')
	email = fields.Char(string='Correo electronico', required=True)
	password = fields.Char(string='Contraseña', required=True)
	phone = fields.Char(string='Telefono')
	user_address = fields.Char(string='Direccion de habitación', required=True)
	work_address = fields.Char(string='Direccion de trabajo')
	nacionality = fields.Char(string='Nacionalidad', required=True)
	gender = fields.Selection([('M', 'Masculino'), ('F', 'Femenino')], string='Genero', required=True)
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
	picture = fields.Image(string='Fotografia', max_width=500, max_height=500, required=True)
	student_certificate = fields.Binary(string='Constancia de estudio')
	worker_certificate = fields.Binary(string='Constancia de trabajo')
	observations = fields.Text(string='Observaciones')