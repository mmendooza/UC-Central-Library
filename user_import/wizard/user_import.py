# -*- coding: utf-8 -*-

import openpyxl
import base64
from io import BytesIO

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

IMPORT_REASON_OPTIONS = [
    ('inscripcion', 'Inscripción'), 
    ('desincorporacion', 'Desincorporación temporal'),
    ('retiro', 'Retiro'), 
    ('egreso', 'Egreso')
]

IMPORT_REASON_CODES   = [code for code, _ in IMPORT_REASON_OPTIONS]

class UserImport(models.TransientModel):
    _name = "user.import"
    _description = "User Import"

    reason = fields.Selection(IMPORT_REASON_OPTIONS, string='Motivo', required=True, default=IMPORT_REASON_CODES[0])
    faculty_id = fields.Many2one('faculty', string='Facultad', required=True)
    school_id = fields.Many2one('school', string="Escuela", domain="[('escu_facu', '=', faculty_id)]")
    state = fields.Selection([('init', 'init'), ('done', 'done')], 'Status', readonly=True, default='init')
    file = fields.Binary('Archivo XLSX', required=True)
    
    def import_file(self):
        
        # Do import stuff
        
        header, rows = self._read_file()
        self._check_fields_exist(header)
        self._execute_import(header, rows)

        # Update state
        self.write({'state': 'done'})

        return False
    
    def _read_file(self):

        def remove_empty_rows(rows, header):
            none_row = (None,) * len(header)
            clean_rows = list(filter(lambda x: x != none_row, rows))
            return clean_rows

        msg = 'Por favor, adjunte un archivo válido.'
        try:
            wb = openpyxl.load_workbook(
                filename=BytesIO(base64.b64decode(self.file)), read_only=True
            )
        except:
            raise UserError(msg)
        
        ws = wb.active
        rows = [row for row in ws.iter_rows(min_row=None, max_row=None, min_col=None, max_col=None, values_only=True) if row]
        
        # Validate that the file contains at least the row for the fields to be updated and one row of data.
        if len(rows) < 2:
            raise UserError(msg)
        header = rows.pop(0)
        rows = remove_empty_rows(rows, header)
        
        # TODO: Verificar la existencia de caracteres invalidos. 
        return header, rows
    
    def _check_fields_exist(self, fields):

        user_obj = self.env['sabi.user']
        for field in fields:
            if not hasattr(user_obj, field):
                raise UserError('La columna %s no existe en la tabla de usuarios del SABI' % field)
    
    def _get_cedu_index(self, fields):
        
        try:
            i = fields.index('usua_cedu')
        except:
            raise UserError("La columna 'usua_cedu' no está en el archivo adjunto.")
        
        return i
    
    def _get_users_cedu(self, fields, users_data):

        i = self._get_cedu_index(fields)
        return list(map(lambda t: str(t[i]), users_data))
    
    def _get_existing_users(self, users_cedu):

        # Busca los usuarios que ya existen y los agrupan por cedula

        return {
            f.usua_cedu: f for f in self.env['sabi.user'].sudo().search([('usua_cedu', 'in', users_cedu)])
        }
    
    def _execute_import(self, fields, users_data):
        
        inactive_users = None
        created_users = None
        updated_users = None

        # MOTIVO 1: INSCRIPCION
        if self.reason == IMPORT_REASON_CODES[0]:

            inactive_users, created_users, updated_users = self._import_by_inscripcion(fields, users_data)

    def _import_by_inscripcion(self, fields, users_data):

        users_to_import = self._get_users_cedu(fields, users_data)
        existing_users = self._get_existing_users(users_to_import)

        # 1. Obtener usuarios que pertenecen a la facultad y escuela seleccionada
        
        target_users = self._get_target_users()

        # 2. Desactivar usuarios no incluidos en la importacion 

        inactive_users = self._deactivate_users(target_users, users_to_import)

        # 3. Crear nuevos ingresos 
        
        filtered_user_data = self._filter_users(fields, users_data, existing_users.keys())
        created_users = self._create_users(fields, filtered_user_data)

        # 4. Actualizar los encontrados
        
        # 4.1. Exluir los usuarios recien creados.
        filtered_user_data = users_data
        if created_users:
            filtered_user_data = self._filter_users(fields, users_data, created_users)

        # 4.2. Obtener el codigo de los usuarios 
        users_to_update = self._get_users_cedu(fields, filtered_user_data)
        if users_to_update:
            users_codi = self._get_users_codi(users_to_update)
            self._update_users(fields, filtered_user_data, users_codi)
        
        return inactive_users, created_users, users_to_update
    
    def _filter_users(self, fields, users_data, existing_users):
        # Excluye los usuarios existentes de los datos de usuarios
        i = self._get_cedu_index(fields) 
        users_data = list(
            filter(lambda x: str(x[i]) not in existing_users, users_data)
        )
        return users_data
    
    def _create_users(self, fields, users_data):

        vals_list = []
        for user_data in users_data:
            vals = {}
            for i in range(len(fields)):
                vals[fields[i]] = user_data[i]
            vals_list.append(vals)
        
        return self.env['sabi.user'].sudo().create(vals_list).mapped('usua_cedu')
    
    def _update_users(self, fields, users_data, target_users):

        if 'usua_codi' not in fields:
            i = self._get_cedu_index(fields) 
            fields = fields + ('usua_codi',)
            users_data = [
                user_data + (target_users[str(user_data[i])],) for user_data in users_data
            ]

        update_sql = f"""
            UPDATE sabi_user AS su
            SET
        """

        # Construir la parte SET de la instrucción
        for i, field in enumerate(filter(lambda x: x != 'usua_codi', fields)):
            update_sql += f"        {field} = vals.{field}"
            if i < len(fields) - 2:
                update_sql += ",\n"

        # Construir la cláusula FROM para combinar con la lista de códigos de usuarios
        update_sql += """
            FROM (VALUES
        """

        # Agregar los valores de registros como una lista de filas
        for i, value in enumerate(users_data):
            update_sql += f"        ({', '.join(['%s']*len(fields))})"
            if i < len(users_data) - 1:
                update_sql += ",\n"

        # Cerrar la cláusula FROM y unirla con la tabla sabi_user usando el campo usua_codi
        update_sql += f"""
            ) AS vals ({', '.join(fields)})
            WHERE su.usua_codi = vals.usua_codi
        """

        params = [value for user_data in users_data for value in user_data]
        self._cr.execute(update_sql, params)
        return True
    
    def _get_target_users(self):

        where_params = [self.faculty_id.facu_codi.lstrip('0')]
        school_where_clause = ''

        if self.school_id:
            school_where_clause = 'AND user.usua_escu = %s'
            where_params.append(self.school_id.escu_codi.lstrip('0'))

        self._cr.execute(f"""
            SELECT usua_cedu
            FROM sabi_user
            WHERE usua_facu = %s {school_where_clause}
            GROUP BY usua_cedu
        """, where_params)

        return [t[0] for t in self._cr.fetchall()] 
    
    def _deactivate_users(self, target_users, users_to_import):

        users_to_deactivate = [u for u in target_users if u not in users_to_import]

        if users_to_deactivate:
            # No requiere aplicar filtrado de facultad y escuela, target_users ya lo esta.
            self.env.cr.execute(f"""
                UPDATE sabi_user SET usua_bloq = 0
                WHERE usua_cedu in %s
            """, [tuple(users_to_deactivate)])
        
        return users_to_deactivate

    def _get_users_codi(self, users_cedu):

        where_params = [self.faculty_id.facu_codi.lstrip('0')]
        school_where_clause = ''

        if self.school_id:
            school_where_clause = 'AND user.usua_escu = %s'
            where_params.append(self.school_id.escu_codi.lstrip('0'))

        if users_cedu:
            cedu_where_clause = 'AND usua_cedu in %s'
            where_params.append(tuple(users_cedu))

        self._cr.execute(f"""
            SELECT usua_codi, usua_cedu
            FROM sabi_user
            WHERE usua_facu = %s {school_where_clause} {cedu_where_clause}
        """, where_params)

        return {t[1]: t[0] for t in self._cr.fetchall()} 
