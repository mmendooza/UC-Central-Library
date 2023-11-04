# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SabiUser(models.Model):
	_name = "sabi.user"
	_description = "Usuario SABI"

	usua_codi = fields.Integer(string='Identificador de línea') #TO DO: evaluar lo del auto incremento
	usua_cedu = fields.Char(string='Cédula de identidad')
	usua_nomb = fields.Char(string='Nombre y apellido')
	usua_tipo = fields.Char(string='Tipo de usuario')
	usua_facu = fields.Char(string='Facultad')
	usua_escu = fields.Char(string='Escuela')
	usua_menc = fields.Char(string='Mención')
	usua_unid = fields.Char(string='Unidad de Información')
	usua_sexo = fields.Char(string='Género')
	usua_disc = fields.Char(string='Discapacidad')
	usua_trab = fields.Char(string='Dirección de trabajo')
	usua_habi = fields.Char(string='Dirección de Habitación')
	usua_bloq = fields.Integer(string='Usuario bloqueado')
	usua_carn = fields.Integer(string='Carnet')
	usua_ano = fields.Integer(string='Año en curso')
	usua_secc = fields.Char(string='Sección a la que pertence')
	usua_foto = fields.Image(string='Fotografía referencia', max_width=500, max_height=500)
	usua_ucre = fields.Char(string='Usuario crea registro') 	
	usua_crea = fields.Datetime(string='Fecha de creación')     					
	usua_umod = fields.Char(string='Último usuario modifica')		
	usua_modi = fields.Datetime(string='Última fecha que se modificó')  
	usua_obse = fields.Char(string='Observación')
	usua_peri = fields.Char(string='usua_peri???')
	usua_edcv = fields.Char(string='Estado civil')
	usua_cdac = fields.Char(string='usua_cdac???')
	usua_nive = fields.Char(string='usua_nive???')
	usua_naci = fields.Char(string='Fecha de nacimiento')
	usua_anio = fields.Char(string='usua_anio???')
	usua_telf = fields.Char(string='Teléfono')
	usua_dire = fields.Char(string='Dirección')
	usua_corr = fields.Char(string='Correo')
	usua_etiq = fields.Char(string='Etiqueta foránea')
	usua_inst = fields.Char(string='Etiqueta institución')
	usua_etvi = fields.Char(string='Etiqueta visible en carnets')
	usua_nada = fields.Char(string='Nacionalidad')
	internal_user_id = fields.Many2one('internal.user', index=True, ondelete='cascade', string='Usuario Interno') # TO DO: Proponer este campo nuevo
	usua_state = fields.Selection([ # TO DO: Proponer este campo nuevo
		('new', 'Nuevo Ingreso'),
		('regular', 'Regular'),
		('graduated', 'Egresado'),
		('retired', 'Retirado'),
		('inactive', 'Inactivo'),],
		string='Estado'
	)
	
