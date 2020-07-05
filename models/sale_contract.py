from odoo import api, exceptions, fields, models, _
import time


class SaleContract(models.Model):
    _name = "sale.contract"

    @api.multi
    def _cek_fe(self):
        for contract in self:
            if contract.fe_spec_to < contract.fe_spec_from :
                return False 

        return True
    
    @api.multi
    def _cek_moisture(self):
        for contract in self:
            if contract.moisture_spec_to < contract.moisture_spec_from :
                return False 

        return True

    @api.multi
    def _cek_mineral(self):
        for contract in self:
            if contract.mineral_spec_to < contract.mineral_spec_from :
                return False 

        return True

    name = fields.Char(string="Name", size=100 , required=True)
    start_date = fields.Date('Start Date', help='',  default=time.strftime("%Y-%m-%d") )
    end_date = fields.Date('End Date', help='',  default=time.strftime("%Y-%m-%d") )
    base_price = fields.Float( string="Base Price", required=True, default=0, digits=0 )
    quantity = fields.Float( string="Quantity (WMT)", required=True, default=0, digits=0 )

    ni_spec = fields.Float( string="Ni Specification (%)", required=True, default=0, digits=0 )
    fe_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    fe_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )
    moisture_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    moisture_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )
    mineral_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    mineral_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )


    _constraints = [ 
        (_cek_fe, 'Spesifikasi Fe Tidak Valid', ['fe_spec_from','fe_spec_to'] ) ,
        (_cek_moisture, 'Spesifikasi Moisture Tidak Valid', ['moisture_spec_from','moisture_spec_to'] ),
        (_cek_mineral, 'Spesifikasi SiO2/MgO Tidak Valid', ['mineral_spec_from','mineral_spec_to'] )
        ]
