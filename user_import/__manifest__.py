# -*- coding: utf-8 -*-
{
	'name': "Importación de usuarios",
	'summary': """
		Actualizacion y creacion de usuarios de acuerdo a reglas de la DGBC UC.""",
	'author': "FACyT / Computer science",
	'website': "http://www.facyt.uc.edu.ve/",
	'category': 'Technical',
	'depends': ['models_definition', 'base_import'],
	'data': [
        'security/ir.model.access.csv',
        'views/user_import_views.xml',
        'report/user_import_report.xml',
        'report/user_import_templates.xml'
	],
	'license': 'Other proprietary',
}
