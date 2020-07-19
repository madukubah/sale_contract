 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):
	# _name = "res.partner"
	_inherit = "res.partner"

	park_industry_id = fields.Many2one(
		'sale.park.industry', 
		string='Park Industry', 
		index=True,
        store=True
		)

	contract_id = fields.Many2one(
		'sale.contract',
		string='Contract', 
        store=True
		)