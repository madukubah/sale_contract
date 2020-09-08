from odoo import api, exceptions, fields, models, _
import time
from datetime import datetime
from odoo.addons import decimal_precision as dp

class ContractElementSpec(models.Model):
    _name = "sale.contract.element.spec"

    sale_contract_id = fields.Many2one("sale.contract", string="Contract", ondelete="cascade" )

    element_id = fields.Many2one("qaqc.chemical.element", required=True, string="Element", ondelete="restrict" )
    rules = fields.One2many(
        'sale.contract.element.spec.rule',
        'element_spec_id',
        string='Rules',
        copy=True )
    
    def _compute_price_based_on_rules( self, _coa_element_spec ):
        for rule in self.rules :
            diff = abs( _coa_element_spec.spec - rule.spec )
            levels = diff / rule.level
            if rule.rule == "<" :
                if _coa_element_spec.spec < rule.spec:
                    return {
                        'name': rule.name,
                        'price': rule.price * levels,
                    }
            if rule.rule == "<=" :
                if _coa_element_spec.spec <= rule.spec:
                    return {
                        'name': rule.name,
                        'price': rule.price * levels,
                    }
            if rule.rule == ">" :
                if _coa_element_spec.spec > rule.spec:
                    return {
                        'name': rule.name,
                        'price': rule.price * levels,
                    }
            if rule.rule == ">=" :
                if _coa_element_spec.spec >= rule.spec:
                    return {
                        'name': rule.name,
                        'price': rule.price * levels,
                    }

        return {
            'name': "None",
            'price': 0,
        }
        

    
class ContractElementSpecRule(models.Model):
    _name = "sale.contract.element.spec.rule"

    element_spec_id = fields.Many2one("sale.contract.element.spec", string="Element Spec", ondelete="cascade" )

    name = fields.Char(string="Name", size=100 , required=True)
    rule = fields.Selection([
        ('<', '<'),
        ('<=', '<='),
        ('>', '>'),
        ('>=', '>='),
        ], string='Rule', required=True, copy=True, index=True, track_visibility='onchange' )
    spec = fields.Float( string="Specification (%)", required=True, default=0, digits=dp.get_precision('Contract') )
    price = fields.Float( string="Price (USD)", required=True, default=0, digits=dp.get_precision('Contract') )
    level = fields.Float( string="Levels", required=True, default=0, digits=dp.get_precision('Contract') )

    