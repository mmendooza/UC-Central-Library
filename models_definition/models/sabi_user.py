# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InternUserHistorial(models.Model):
	_name = "sabi.user"
	_description = "Usuario SABI"

	usua_codi = fields.Integer(string='Identificador de línea', required=True) #TO DO: evaluar lo del auto incremento
	usua_cedu = fields.Char(string='Cédula de identidad')
	usua_nomb = fields.Char(string='Nombre y apellido')
	usua_tipo = fields.Selection([
		('student', 'Estudiante'),
		('professor', 'Docente'),
		('administrative', 'Personal administrativo'),
		('laborer', 'Personal obrero')],
		string='Tipo de usuario',
		required=True
	)
	usua_facu = fields.Many2one('faculty', string='Facultad')
	usua_escu = fields.Many2one('school', string='Escuela')
	usua_menc = fields.Many2one('mention', string='Mención')
	usua_unid = fields.Many2one('information.unit', string='Unidad de Información')
	usua_sexo = fields.Selection([
		('m', 'M'),
		('f', 'F'),],
		string='Género',
		required=True
	)
	usua_disc = fields.Selection([
		('none', 'Ninguna'),
		('hearing', 'Auditiva'),
		('lenguage', 'De lenguaje'),
		('physical', 'Física'),
		('intellectual', 'Intelectual'),
		('motor', 'Motríz'),
		('multiple', 'Múltiple'),
		('visual', 'Visual')],
		string='Discapacidad',
		default='none',
		required=True
	)
	usua_trab = fields.Char(string='Dirección de trabajo')
	usua_habi = fields.Char(string='Dirección de Habitación')
	usua_bloq = fields.Boolean(string='Usuario bloqueado', default=False) #TO DO: preguntar si este campo puede ser booleano
	usua_carn = fields.Many2one('carnet', string='Carnet')
	usua_ano = fields.Integer(string='Año en curso')
	usua_secc = fields.Char(string='Sección a la que pertence')
	usua_foto = fields.Image(string='Fotografía referencia', max_width=500, max_height=500, required=True)
	usua_ucre = fields.Many2one('res.users', string='Usuario crea registro') 	#TO DO: preguntar si este campo puede ser reemplazado por el de Odoo
	usua_crea = fields.Date(string='Fecha de creacion')     					#TO DO: preguntar si este campo puede ser reemplazado por el de Odoo
	usua_umod = fields.Many2one('res.users',string='Último usuario modifica')	#TO DO: preguntar si este campo puede ser reemplazado por el de Odoo	
	usua_modi = fields.Date(string='Última fecha que se modificó')  
	usua_obse = fields.Char(string='Observación')
	usua_peri = fields.Char(string='usua_peri???')
	usua_edcv = fields.Char(string='Estado civil')
	usua_cdac = fields.Char(string='usua_cdac???')
	usua_nive = fields.Char(string='usua_nive???')
	usua_naci = fields.Date(string='Fecha de nacimiento')
	usua_anio = fields.Char(string='usua_anio???')
	usua_telf = fields.Char(string='Teléfono')
	usua_dire = fields.Char(string='Dirección')
	usua_corr = fields.Char(string='Correo')
	usua_etiq = fields.Char(string='Etiqueta foránea')
	usua_inst = fields.Char(string='Etiqueta institución')
	usua_etvi = fields.Char(string='Etiqueta visible en carnets')
	usua_nada = fields.Many2one('res.country', string='Nacionalidad')
	internal_user_id = fields.Many2one('internal.user', index=True, ondelete='cascade') # TO DO: Proponer este campo nuevo
	usua_state = fields.Selection([ # TO DO: Proponer este campo nuevo
		('new', 'Nuevo Ingreso'),
		('regular', 'Regular'),
		('graduated', 'Egresado'),
		('retired', 'Retirado'),
		('inactive', 'Inactivo'),],
		string='Estado',
		required=True
	)
	
