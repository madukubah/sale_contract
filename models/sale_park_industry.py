from odoo import api, exceptions, fields, models, _


class SaleParkIndustry(models.Model):
    _name = "sale.park.industry"

    name = fields.Char(string="Name", size=100 , required=True)
    # currency_80_pc = fields.Float( string="Currency 80%", required=True, default=0 )
    # currency_20_pc = fields.Float( string="Currency 20%", required=True, default=0 )
    factories_ids = fields.One2many(
        'res.partner', 
        'park_industry_id', 
        string='Factory lines',
        copy=True)