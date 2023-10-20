# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import format_datetime

from ..wizard.user_import import IMPORT_REASON_OPTIONS
from ..wizard.user_import import IMPORT_EXCLUSION_REASON

class UserImportReport(models.AbstractModel):

    _name = 'report.user_import.report_userimport'

    def _get_reason(self, technical_reason_name):
        
        reason_description = False
        for reason in IMPORT_REASON_OPTIONS:
            if reason[0] == technical_reason_name:
                reason_description = reason[1]
                break 

        return reason_description
    
    def _get_datetime(self, date_str):

        date = format_datetime(
            env = self.env, 
            value = fields.Datetime.from_string(date_str),
            tz = self.env.context.get('tz'), 
            dt_format="dd/MM/yyyy HH:mm:ss"
        ) 

        return date
    
    def _get_users_data(self, users, reason=None):
        
        users_data = dict()
        users_recs = self.env['sabi.user'].search([('usua_cedu', 'in', users)])

        for user in users_recs:
            users_data[user.usua_cedu] = {
                'usua_nomb': user.usua_nomb,
                'usua_facu': user.usua_facu,
                'usua_escu': user.usua_escu

            }
        
        return users_data
    
    def _get_excluded_users(self, reasons, import_data):
        
        users = dict()
        if len(reasons.get('cedu')) > 0:
            for k,v in reasons.get('reason').items():
                if v:
                    reason_display_name = next(filter(lambda x: x[0] == k, IMPORT_EXCLUSION_REASON))[1]
                    if k != IMPORT_EXCLUSION_REASON[2][0]: 
                        users[reason_display_name] = self._get_users_data(v)
                    else:
                        # Tomar datos del archivo
                        
                        nomb_idx = self.env['user.import']._get_field_index('usua_nomb', import_data['fields'])
                        users[reason_display_name] = dict()
                        for cedu in v:
                            users[reason_display_name][cedu] = {
                                'usua_nomb': import_data['users_data'][cedu][nomb_idx]
                            }
        return users
    
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError("Falta el contenido del formulario, este informe no se puede imprimir.")

        import_report = self.env['ir.actions.report']._get_report_from_name('user_import.report_userimport')

        return {
            'doc_model': import_report.model,
            'get_reason': self._get_reason(data['form']['reason']),
            'get_reason_technical_name': data['form']['reason'],
            'get_datetime': self._get_datetime(data['form']['write_date']),
            'get_faculty': data['form']['faculty_id'] and data['form']['faculty_id'][1],
            'get_school': data['form']['school_id'] and data['form']['school_id'][1] or 'No seleccionada',
            'get_user_count_before_import': data['import_results']['user_count_before_import'],
            'get_users_count_in_importfile': len(data['import_results']['file_data']['users_data']),
            'get_user_count_after_import': data['import_results']['user_count_after_import'],
            'get_created_users_count': 
                len(data['import_results'].get('created_users', [])),
            'get_created_users_data': 
                self._get_users_data(data['import_results'].get('created_users'),
                    data['form']['reason']),
            'get_updated_users_count': 
                len(data['import_results'].get('updated_users', [])),
            'get_updated_users_data': 
                self._get_users_data(list(data['import_results'].get('updated_users', dict()).keys()),
                    data['form']['reason']),
            'get_inactive_users_count': 
                len(data['import_results'].get('inactive_users', [])),
            'get_inactive_users_data': 
                self._get_users_data(data['import_results'].get('inactive_users', []),
                    data['form']['reason']),
            'get_excluded_users_count': 
                len(data['import_results'].get('excluded_users', dict()).get('cedu')),
            'get_excluded_users_data': 
                self._get_excluded_users(
                    data['import_results'].get('excluded_users', dict()), 
                    data['import_results']['file_data']
                )
        }
