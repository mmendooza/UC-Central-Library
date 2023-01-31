# -*- coding: utf-8 -*-
{
	'name': "Models definition",
	'summary': """Centralized definition of the set of models that make up the UC library card system.""",
	'author': "FACyT / Computer science",
	'website': "http://www.facyt.uc.edu.ve/",
	'category': 'Technical',
	'depends': ['base','mail','portal' ,'territorial_pd'],
	'data': [
		'security/ir.model.access.csv',
		'views/models_definition_views.xml',
		'views/models_definition_actions.xml',
		'views/models_definition_menu.xml',
	],
	'license': 'Other proprietary',
}
