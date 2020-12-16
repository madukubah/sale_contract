from odoo import api, exceptions, fields, models, _
import time
from datetime import datetime
from odoo.addons import decimal_precision as dp

class ContractBasePriceComponent(models.Model):
    _name = "sale.contract.base.price.component"

    sale_contract_id = fields.Many2one("sale.contract", string="Contract", ondelete="cascade" )
    rule = fields.Selection([
        ('main', 'Main'),
        ('add', 'Addition'),
        ('subtract', 'Subtraction'),
        ], string='Rule', required=True, copy=True, index=True, track_visibility='onchange' )
    element_id = fields.Many2one("qaqc.chemical.element", required=True, string="Element", ondelete="restrict" )
    spec = fields.Float( string="Specification (%)", required=True, default=0, digits=dp.get_precision('Contract') )