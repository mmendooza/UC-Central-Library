# -*- coding: utf-8 -*-

import openpyxl
import base64
from io import BytesIO
from collections import Counter
from psycopg2 import sql


from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError



IMPORT_REASON_OPTIONS = [
    ('inscripcion_nuevo', 'Inscripción nuevo ingreso'), 
    ('inscripcion_regular', 'Inscripción regular'), 
    ('desincorporacion', 'Desincorporación temporal'),
    ('retiro', 'Retiro'), 
    ('egreso', 'Egreso'),
    ('inscripcion_doble_carrera', 'Inscripción solo doble carrera')
]

IMPORT_EXCLUSION_REASON = [
    ('existe', 'Existe en la misma carrera'),
    ('otra_facultad', 'Aparece en otra facultad'),
    ('otra_carrera', 'Aparece en otra carrera de la misma facultad'),
    ('no_existente', 'No aparece en el sistema'),
    ('no_doble_carrera', 'No aparece en más de una carrera'),
    ('doble_carrera_misma_facu', 'Doble carrera en la misma facultad')
]

class UserImport(models.TransientModel):
    _name = "user.import"
    _description = "User Import"

    reason = fields.Selection(IMPORT_REASON_OPTIONS, 
        string='Motivo', 
        default=IMPORT_REASON_OPTIONS[0][0], 
        states={'done': [('readonly', True)]}
    )
    faculty_id = fields.Many2one('faculty', 
        string='Facultad', 
        states={'done': [('readonly', True)]}
    )
    school_id = fields.Many2one('school', 
        string="Escuela", 
        domain="[('escu_facu', '=', faculty_id)]", 
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection([('init', 'init'), ('done', 'done')], 
        string='Status', 
        readonly=True, 
        default='init', 
        states={'done': [('readonly', True)]}
    )
    file = fields.Binary('Archivo XLSX', 
        required=True, 
        states={'done': [('readonly', True)]}
    )
    
    def import_file(self):
        
        # Do import stuff
        
        header, rows = self._read_file()
        import_results = self._execute_import(header, rows)

        # Update state
        self.write({'state': 'done'})
        context = dict(
            self.env.context, 
            import_results = import_results,
            hide_created_button = len(import_results.get('created_users', [])) == 0,
            hide_updated_button = len(import_results.get('updated_users', [])) == 0,
            hide_inactive_button = len(import_results.get('inactive_users', [])) == 0,
            hide_excluded_button = not (import_results.get('excluded_users', False) \
                and len(import_results['excluded_users']['cedu']) > 0
            ), 
        )

        # Return wizard otherwise it will close wizard and will not show result message to user.
        return {
            'name': 'Importar Usuarios',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'res_model': 'user.import',
            'type': 'ir.actions.act_window',
            'context': context
        }

    def _read_file(self):

        def has_immutable_fields(header):
            immutable_fields = ['usua_codi', 'usua_foto']
            for field in immutable_fields:
                if field in header:
                    raise UserError('El campo %s no debe ser modificado por importacion. '
                        'Remueva la columna correspondiente en el archivo.' % field)
        
        def remove_empty_rows(rows, header):
            none_row = (None,) * len(header)
            clean_rows = list(filter(lambda x: x != none_row, rows))
            return clean_rows
        
        def check_empty_columns(rows, header):

            for field in header:
                field_vals = list(self._get_field_data(field, header, rows))
                if len(field_vals) == 1 and field_vals[0] == 'None':
                    raise UserError('La columna %s esta vacia. Remueva las columnas vacías del archivo.' % field)
                
            non_nullable_fields = get_non_nullable_fields()
            for row in rows:
                for i, value in enumerate(row):
                    if value is None and header[i] in non_nullable_fields:
                        raise UserError('La columna %s no debe contener celdas vacias.'
                            ' Asegurese que la columna esté llena.' % header[i])
        
        def get_non_nullable_fields():
            # Define una lista de los campos enteros en la tabla sabi.user
            # a los que no se permite establecer un valor None mediante importacion 
            return [
                'id', 'usua_bloq', 'usua_carn', 'usua_codi'
            ]
        
        def check_duplicate_columns(header):
            
            # Compara las longitudes
            if len(header) != len(set(header)):

                counts = Counter(header)
                duplicated_columns = [e for e, count in counts.items() if count > 1]
                raise UserError('La columna %s se encuentra duplicada.' % duplicated_columns[0])
        
        def check_selected_faculty(rows, header):
            usua_facu = list(self._get_field_data('usua_facu', header, rows))
            if len(usua_facu) != 1 or usua_facu[0].lstrip('0') != self.faculty_id.facu_codi.lstrip('0'):
                raise UserError('La facultad seleccionada debe coincidir con toda la columna usua_facu en el archivo.')
        
        def check_selected_school(rows, header):
            usua_escu = self._get_field_data('usua_escu', header, rows)
            usua_escu = {e.lstrip('0') for e in usua_escu}
            if self.school_id:
                if len(usua_escu) != 1 or list(usua_escu)[0] != self.school_id.escu_codi.lstrip('0'):
                    raise UserError('La escuela seleccionada debe coincidir con toda la columna usua_escu en el archivo.')
            else:
                target_schools_codi = self.env['school'].search([('escu_facu', '=', self.faculty_id.id)]).mapped('escu_codi')
                target_schools_codi = [s.lstrip('0') for s in target_schools_codi]
                school_difference = list(set(usua_escu).difference(target_schools_codi))
                if school_difference:
                    raise UserError('La escuela %s en la columna usua_escu del archivo, no pertenece a la facultad seleccionada.' % school_difference[0])
                
        def prepare_update_values(rows, header):
            user_obj = self.env['sabi.user']
            fixed_rows = []
            for row in rows:
                fixed_row = []
                for i, value in enumerate(row):
                    if user_obj._fields[header[i]].type != 'datetime':
                        new_val = user_obj._fields[header[i]].convert_to_column(value, user_obj) 
                    else:
                        new_val = value    
                    fixed_row.append(new_val)
                fixed_rows.append(tuple(fixed_row))
                

            return fixed_rows
        
        def check_duplicated_users(rows, header):
            cedu_idx = self._get_field_index('usua_cedu', header)
            cedu_frequency = {}
            repeated_cedu = []

            # Count the frequency of each number in the list of tuples
            for row in rows:
                number = row[0]
                if row[cedu_idx] in cedu_frequency:
                    cedu_frequency[row[cedu_idx]] += 1
                    if cedu_frequency[row[cedu_idx]] == 2:
                        repeated_cedu.append(str(row[cedu_idx]))
                else:
                    cedu_frequency[number] = 1
            if repeated_cedu:
                raise UserError('Los usuarios con las siguientes cedulas se encuentran duplicados en el archivo:\n\n%s' 
                    % ', '.join(repeated_cedu) )

        msg = 'Por favor, adjunte un archivo válido.'
        try:
            wb = openpyxl.load_workbook(
                filename=BytesIO(base64.b64decode(self.file)), read_only=True
            )
        except:
            raise UserError(msg)
        
        ws = wb.active
        rows = [row for row in ws.iter_rows(min_row=None, max_row=None, min_col=None, max_col=None, values_only=True) if row]
        
        # Validations: If these detect an error, the file is not accepted before starting the import.

        # 1. Validate that the file contains at least the row for the fields to be updated and one row of data.
        if len(rows) < 2:
            raise UserError(msg)
        
        header = rows.pop(0)

        # 2. Validates that the header contains a consecutive sequence of field names
        for i in range(0, len(header)):
            if not header[i]:
                raise UserError(("El archivo contiene %d columnas pero la columna %d no contiene un nombre de campo.\n\n%s")
                    % (len(header), i+1, msg)
                )
            elif not self.env['sabi.user']._fields.get(header[i], False):  
                raise UserError(("La columna %s no tiene un campo en la tabla de usuarios.\n\nPor favor, corrija el nombre de la columna.")
                    % header[i]
                )
        
        # 3. Verificar si el archivo incluye campos NO actualizables por importacion 
        has_immutable_fields(header)

        # 4. Verificar la inclusion de columnas obligatorias
        mandatory_fields = ['usua_cedu', 'usua_facu', 'usua_escu']
        for field in mandatory_fields:
            self._get_field_index(field, header)
        
        rows = remove_empty_rows(rows, header)

        # 5. Verificar que la facultad seleccionada sea la unica en el archivo
        check_selected_faculty(rows, header)
        
        # 6. Verificar que las escuelas pertenezcan a la facultad seleccionada
        check_selected_school(rows, header)
        
        # 7. Remover columnas repetidas, dejado la ultima
        check_duplicate_columns(header)

        # 8. Revisar columnas vacias
        check_empty_columns(rows, header)

        # 9. Verificar si hay usuarios repetidos en el archivo 
        check_duplicated_users(rows, header)

        # 10. Convertir valores para actualizacion
        rows = prepare_update_values(rows, header)

        # TODO: Verificar la existencia de caracteres invalidos. 
        return header, rows
    
    def _execute_import(self, fields, users_data):

        pre_import_data = {
            'file_data': {
                'fields': fields,
                'users_data': self._get_users_data_dict(fields, users_data),
            },
            'user_count_before_import': self._get_user_count()
        }

        # MOTIVO: INSCRIPCION NUEVO INGRESO
        if self.reason == IMPORT_REASON_OPTIONS[0][0]:

            import_results = self._import_by_inscripcion_nuevo(fields, users_data)

        # MOTIVO: INSCRIPCION REGULAR
        elif self.reason == IMPORT_REASON_OPTIONS[1][0]:

            import_results = self._import_by_inscripcion_regular(fields, users_data)
        elif self.reason in \
            (IMPORT_REASON_OPTIONS[2][0], IMPORT_REASON_OPTIONS[3][0],IMPORT_REASON_OPTIONS[4][0]):

            import_results = self._import_by_egreso_retiros(fields, users_data)
        # MOTIVO: INSCRIPCION DOBLE CARRERA
        elif self.reason == IMPORT_REASON_OPTIONS[5][0]:
            import_results = self._import_by_double_career(fields, users_data)
        
        import_results.update(pre_import_data)
        import_results.update({
            'user_count_after_import': self._get_user_count(),
        })
    
        return import_results

    def _import_by_inscripcion_nuevo(self, fields, users_data):
        
        created_users = dict()
        users_to_create = self._get_users_data_dict(fields, users_data)
        
        # 1. Obtener los usuarios a crear que ya existen 
        existing_users = self._get_existing_users(users_to_create.keys())

        # 2. Excluir usuarios que ya existen 

        excluded_users = self._exclude_users(fields, users_to_create, existing_users)

        # 3. Crear nuevos ingresos 

        users_to_create = self._filter_users(users_to_create, excluded_users.get('cedu'))
        created_users = self._create_users(fields, users_to_create)

        return {
            'created_users': created_users,
            'excluded_users': excluded_users,
        }
    
    def _import_by_inscripcion_regular(self, fields, users_data):
        
        users_to_update = self._get_users_data_dict(fields, users_data)

        # 1. Obtener usuarios existentes 
        existing_users = self._get_existing_users(users_to_update.keys())

        # 2. Excluir usuarios

        excluded_users = self._exclude_users(fields, users_to_update, existing_users)
        users_to_update = self._filter_users(users_to_update, excluded_users.get('cedu'))
        
        # 3. Desactivar usuarios 
        
        # No incluidos en la importacion 

        inactive_users = self._deactivate_users(users_to_update, excluded_users)

        # 4. Actualizar los encontrados

        if users_to_update:
            self._update_users(fields, users_to_update)
        
        return {
            'updated_users': users_to_update,
            'inactive_users': inactive_users,
            'excluded_users': excluded_users,
        }
    
    def _import_by_egreso_retiros(self, fields, users_data):

        inactive_users = dict()
        users_to_update = self._get_users_data_dict(fields, users_data)

        # 1. Obtener los usuarios a actualizar que ya existen 
        
        existing_users = self._get_existing_users(users_to_update.keys())

        # 2. Excluir los usuarios no existentes y que aparezcan en mas de una carrera

        excluded_users = self._exclude_users(fields, users_to_update, existing_users)

        # 3. Filtrar los usuarios a actualizar, dejando solo los que existen.

        if excluded_users.get('cedu'):
            users_to_update = self._filter_users(users_to_update, excluded_users.get('cedu'))
            
        # 4. Desactivar usuarios 
        if users_to_update:
            self._update_users(fields, users_to_update)
            inactive_users = self._deactivate_users(users_to_update)

        return {
            'updated_users': users_to_update,
            'inactive_users': inactive_users,
            'excluded_users': excluded_users,
        }

    def _import_by_double_career(self, fields, users_data):

        created_users = dict()
        users_to_update = self._get_users_data_dict(fields, users_data)

        # 1. Obtener los usuarios a actualizar que ya existen 
        
        existing_users = self._get_existing_users(users_to_update.keys())

        # 2. Excluir los usuarios no existentes y que no parezcan en almenos dos carreras

        excluded_users = self._exclude_users(fields, users_to_update, existing_users)
        users_to_update = self._filter_users(users_to_update, excluded_users.get('cedu'))
        
        # 3. Si no existen ocurrencias asociadas a la carrera que esta llegando en el archivo, crearla

        # Primero excluye las ocurrencias que ya existen
        
        users_with_existing_occurrences = self._get_user_occurrences_by_career(users_to_update, fields)
        missing_occurrences = self._filter_users(users_to_update, users_with_existing_occurrences)
        if missing_occurrences:
            created_users = self._create_users(fields, missing_occurrences)
    
        # 4. Si existen, actualizar ocurrencias que coincida con la carrera del archivo de importacion
        
        # Primero excluye los usuarios recien creados.
        if created_users:
            users_to_update = self._filter_users(users_to_update, created_users)

        if users_to_update:
            self._update_users(fields, users_to_update)
        
        return {
            'created_users': created_users,
            'updated_users': users_to_update,
            'excluded_users': excluded_users,
        }
    
    def _get_field_index(self, field_name, fields):
        
        try:
            i = fields.index(field_name)
        except:
            raise UserError(("La columna %s no está en el archivo adjunto.") % field_name)
        
        return i
    
    def _get_field_data(self, field_name, fields, users_data):

        i = self._get_field_index(field_name, fields)
        return set(map(lambda t: str(t[i]), users_data))
    
    def _get_existing_users(self, users_cedu):

        # Busca los usuarios que ya existen y los agrupan por cedula
        
        self._cr.execute(f"""
            SELECT usua_cedu, usua_nomb, usua_codi, usua_facu, usua_escu, usua_menc, usua_bloq
            FROM sabi_user
            WHERE usua_cedu in %s
        """, [tuple(users_cedu)])

        existing_users = {}
        for user in self.env.cr.dictfetchall():
            usua_cedu = user.get('usua_cedu')
            
            if usua_cedu in existing_users:
                existing_users[usua_cedu].append(user)
            else:
                existing_users[usua_cedu] = [user]
        
        return existing_users

    def _filter_users(self, users_data, existing_users):
        # Excluye los usuarios existentes de los datos de usuarios
        
        data = users_data.copy()
        for existing_user in filter(lambda x: x in data, existing_users): 
            data.pop(existing_user)
        
        return data
    
    def _create_users(self, fields, users_data):

        vals_list = []
        for user_data in users_data.values():
            vals = {}
            for i in range(len(fields)):
                vals[fields[i]] = user_data[i]
            # Establecer el usuario como ACTIVO, a traves del campo usua_bloq: '0: Activo; 1:bloqueado'
            vals['usua_bloq'] = 0
            vals_list.append(vals)
        
        return self.env['sabi.user'].sudo().create(vals_list).mapped('usua_cedu')
    
    def _update_users(self, fields, users_data):

        update_sql = f"""
            UPDATE sabi_user AS su
            SET
        """

        # Construir la parte SET de la instrucción
        for i, field in enumerate(fields):
            update_sql += f"        {field} = vals.{field}"
            if i < len(fields) - 1:
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
        
        where_clause = 'su.usua_cedu = CAST(vals.usua_cedu AS VARCHAR)'
        
        if self.reason == IMPORT_REASON_OPTIONS[5][0]:
            # Extiende la clausula where si es una importacion por doble carrera,
            # para actualizar el usuario en la carrera que esta llegando por importacion
            # esto evita crear nuevamente el usuario para la misma carrera!

            where_clause += " AND TRIM(LEADING '0' FROM su.usua_facu) = TRIM(LEADING '0' FROM CAST(vals.usua_facu AS VARCHAR)) " +  \
                "AND TRIM(LEADING '0' FROM su.usua_escu) = TRIM(LEADING '0' FROM CAST(vals.usua_escu AS VARCHAR))"
        
        update_sql += f"""
            ) AS vals ({', '.join(fields)})
            WHERE {where_clause}
        """

        params = [value for user_data in users_data.values() for value in user_data]
        self._cr.execute(update_sql, params)
        return True
    
    def _exclude_users(self, fields, users_data, existing_users):

        def is_double_career_on_same_facu(careers_by_facu):
            k = self.faculty_id.facu_codi.lstrip('0')           
            return len(careers_by_facu.get(k)) > 1

        def exclude_by_existence(excluded_users, cedu):

            excluded_users['cedu'].append(cedu)
            excluded_users['reason'][IMPORT_EXCLUSION_REASON[0][0]].append(cedu)

        def exclude_by_another_faculty(excluded_users, cedu):

            excluded_users['cedu'].append(cedu)
            excluded_users['reason'][IMPORT_EXCLUSION_REASON[1][0]].append(cedu)

        def exclude_by_another_school(excluded_users, cedu):

            excluded_users['cedu'].append(cedu)
            excluded_users['reason'][IMPORT_EXCLUSION_REASON[2][0]].append(cedu)

        def exlude_by_absence(excluded_users, users_data, existing_users):

            missing_users = set(users_data.keys()) - set(existing_users.keys())
            if missing_users:
                excluded_users['cedu'].extend(list(missing_users))
                excluded_users['reason'][IMPORT_EXCLUSION_REASON[3][0]].extend(list(missing_users))

        def exclude_by_no_double_career(excluded_users, cedu):

            excluded_users['cedu'].append(cedu)
            excluded_users['reason'][IMPORT_EXCLUSION_REASON[4][0]].append(cedu)

        def exclude_by_double_career_on_same_faculty(excluded_users, cedu):

            excluded_users['cedu'].append(cedu)
            excluded_users['reason'][IMPORT_EXCLUSION_REASON[5][0]].append(cedu)

        ###########################################################################################

        cedu_idx = self._get_field_index('usua_cedu', fields)
        facu_idx = self._get_field_index('usua_facu', fields)
        escu_idx = self._get_field_index('usua_escu', fields)

        excluded_users = {
            'reason': {reason[0]: [] for reason in IMPORT_EXCLUSION_REASON},
            'cedu': [] 
        }
        
        # 1. Inscripcion nuevos ingresos
        if self.reason == IMPORT_REASON_OPTIONS[0][0]:
            for user_occurrences in existing_users.values():
                user = user_occurrences[0]
                user_data = users_data.get(user["usua_cedu"]) 

                # Aparece en otra facultad
                if user["usua_facu"].lstrip('0') != str(user_data[facu_idx]).lstrip('0'):

                    exclude_by_another_faculty(excluded_users, user["usua_cedu"])
                    
                # Aparece en otra escuela 
                elif user["usua_escu"].lstrip('0') != str(user_data[escu_idx]).lstrip('0'):

                    exclude_by_another_school(excluded_users, user["usua_cedu"])
                else:
                #Aparece en la misma escuela

                    exclude_by_existence(excluded_users, user["usua_cedu"])

        # 2. Inscripcion regulares
        elif self.reason == IMPORT_REASON_OPTIONS[1][0]:

            exlude_by_absence(excluded_users, users_data, existing_users)

            for user_occurrences in existing_users.values():
                for user in user_occurrences:

                    user_data = users_data.get(user["usua_cedu"]) 

                    # Aparece en otra facultad
                    if user["usua_facu"].lstrip('0') != str(user_data[facu_idx]).lstrip('0'):

                        exclude_by_another_faculty(excluded_users, user["usua_cedu"])
                        break
                    
                    # Aparece en otra escuela 
                    elif user["usua_escu"].lstrip('0') != str(user_data[escu_idx]).lstrip('0'):

                        exclude_by_another_school(excluded_users, user["usua_cedu"])
                        break
        # 3. Desincorporacion o retiro o egreso
        elif self.reason in \
            (IMPORT_REASON_OPTIONS[2][0], IMPORT_REASON_OPTIONS[3][0], IMPORT_REASON_OPTIONS[4][0]):
            
            exlude_by_absence(excluded_users, users_data, existing_users)

            for cedu, user_occurrences in existing_users.items():
                
                careers_by_facu = dict()
                for occurrence in user_occurrences:
                    careers_by_facu.setdefault(occurrence['usua_facu'], [])
                    careers_by_facu[occurrence['usua_facu']].append(occurrence['usua_escu'])

                escu = list(map(lambda u: u.get('usua_escu', None), user_occurrences))

                if self.faculty_id.facu_codi.lstrip('0') not in careers_by_facu.keys():

                    # No aparece en la facultad seleccionada
                    exclude_by_another_faculty(excluded_users, cedu)
                elif self.school_id and self.school_id.escu_codi.lstrip('0') not in escu:

                    # No aparece en la escuela seleccionada 
                    exclude_by_another_school(excluded_users, cedu)
                    
                elif not self.school_id and is_double_career_on_same_facu(careers_by_facu):

                    # Doble carrera en la misma facultad y no selecciono escuela (ambiguo)
                    exclude_by_double_career_on_same_faculty(excluded_users, cedu)
        # 4. Inscripción solo doble carrera
        elif self.reason == IMPORT_REASON_OPTIONS[5][0]:
            
            exlude_by_absence(excluded_users, users_data, existing_users)

            # No es doble carrera
            for cedu, user_occurrences in existing_users.items():
                careers = {user.get('usua_escu') for user in user_occurrences}
                user_data = users_data.get(cedu) 
                if len(careers) == 1 and careers.pop() == str(user_data[escu_idx]):

                    exclude_by_no_double_career(excluded_users, cedu)

        return excluded_users
    
    def _get_target_users(self):

        where_params = [self.faculty_id.facu_codi.lstrip('0')]
        school_where_clause = ''

        if self.school_id:
            school_where_clause = "AND TRIM(LEADING '0' FROM usua_escu) = %s"
            where_params.append(self.school_id.escu_codi.lstrip('0'))

        self._cr.execute(f"""
            SELECT usua_cedu
            FROM sabi_user
            WHERE TRIM(LEADING '0' FROM usua_facu) = %s {school_where_clause}
            GROUP BY usua_cedu
        """, where_params)

        return [t[0] for t in self._cr.fetchall()] 
    
    def _deactivate_users(self, users_to_import, excluded_users=None):

        if self.reason == IMPORT_REASON_OPTIONS[1][0]:
            
            # Obtener usuarios que pertenecen a la facultad y escuela seleccionada
            target_users = self._get_target_users()
            
            # Obtener usuarios no incluidos en la importacion 
            users_to_remove = excluded_users['reason']['otra_carrera'] + list(users_to_import.keys())
            users_to_deactivate = tuple(set(target_users) - set(users_to_remove))
        
        elif self.reason in \
            (IMPORT_REASON_OPTIONS[2][0], IMPORT_REASON_OPTIONS[3][0], IMPORT_REASON_OPTIONS[4][0]):
            
            users_to_deactivate = tuple(users_to_import.keys())

        if users_to_deactivate:

            self.env.cr.execute(f"""
                UPDATE sabi_user SET usua_bloq = 1
                WHERE usua_cedu in %s
            """, [users_to_deactivate])
        
        return users_to_deactivate

    def _get_users_data_dict(self, fields, users_data):

        cedu_idx = self._get_field_index('usua_cedu', fields)
        return {str(row[cedu_idx]): row for row in users_data}

    def _get_users_codi(self, users_cedu):

        where_params = [self.faculty_id.facu_codi.lstrip('0')]
        school_where_clause = ''

        if self.school_id:
            school_where_clause = "AND TRIM(LEADING '0' FROM usua_escu) = %s"
            where_params.append(self.school_id.escu_codi.lstrip('0'))

        if users_cedu:
            cedu_where_clause = 'AND usua_cedu in %s'
            where_params.append(tuple(users_cedu))

        self._cr.execute(f"""
            SELECT usua_codi, usua_cedu
            FROM sabi_user
            WHERE TRIM(LEADING '0' FROM usua_facu) = %s {school_where_clause} {cedu_where_clause}
        """, where_params)

        return {t[1]: t[0] for t in self._cr.fetchall()} 

    def _get_user_count(self):

        self._cr.execute("SELECT count(*) as user_count FROM sabi_user")
        return self._cr.dictfetchall()[0].get('user_count')
    
    def _get_user_occurrences_by_career(self, users_data, fields):

        if not users_data:
            return []
        
        idx_list = [self._get_field_index('usua_cedu', fields),
            self._get_field_index('usua_facu', fields),
            self._get_field_index('usua_escu', fields)
        ]

        query = "SELECT usua_cedu FROM sabi_user WHERE "
        query += " OR ".join([
            "(usua_cedu = %s AND TRIM(LEADING '0' FROM usua_facu) = TRIM(LEADING '0' FROM %s) AND TRIM(LEADING '0' FROM usua_escu) = TRIM(LEADING '0' FROM %s))" for _ in users_data
        ])
        params = [str(user_data[i]) for user_data in users_data.values() for i in idx_list]
        self._cr.execute(query, params)
        
        return [r[0] for r in self._cr.fetchall()] 

    def _prepare_report_data(self):

        # Datos del formulario de wizard
        [form_data] = self.read()
        # Resultados de la importacion 
        import_results = self.env.context.get('import_results', False)
        
        return {
            'form': form_data,
            'import_results': import_results
        }
            
    def print_report(self):

        data = self._prepare_report_data()
        return self.env.ref('user_import.action_report_userimport').report_action(None, data=data)
    
    def reload(self):
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }