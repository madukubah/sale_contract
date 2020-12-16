# -*- coding: utf-8 -*-

{
    'name': 'Sale Contract for Mining Industry',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Sales Management',
    'depends': [
        'account',
        'product',
        'sale',
        'mining_qaqc_chemical_element',
    ],
    'data': [
        'views/menu.xml',
        'views/sale_park_industry.xml',
        'views/partner.xml',
        'views/sale_contract.xml',
        "views/contract_element_spec.xml",
        "views/contract_element_spec_rule.xml",
        'views/contract_base_price_component.xml',
        
        "security/ir.model.access.csv",

        "data/contract_data.xml",
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	# "auto_instal": False,
	# "application": True,
}
