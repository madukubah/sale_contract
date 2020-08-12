from odoo import api, exceptions, fields, models, _
import time
from datetime import datetime
from odoo.addons import decimal_precision as dp

class SaleContract(models.Model):
    _name = "sale.contract"
    _order = "id desc"

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
    factory_id	= fields.Many2one('res.partner', string='Factory', required=True, domain=[ ('park_industry_id','!=',False)], ondelete="restrict" )
    park_industry_id = fields.Many2one('sale.park.industry', related="factory_id.park_industry_id", string='Park Industry', readonly=True,  ondelete="restrict" )

    start_date = fields.Date('Start Date', help='',  default=time.strftime("%Y-%m-%d") )
    end_date = fields.Date('End Date', help='',  default=time.strftime("%Y-%m-%d") )
    is_expired = fields.Boolean( string="Progress", readonly=True, default=False, compute="_set_is_expired" )
    quantity = fields.Float( string="Quantity (WMT)", required=True, default=0, digits=0 )

    base_price = fields.Float( string="Base Price (USD)", required=True, default=0, digits=0 )

    ni_spec = fields.Float( string="Ni Specification (%)", required=True, default=0, digits=dp.get_precision('Contract') )
    ni_price_adjustment_bonus = fields.Float( string="Nickel Price Adjustment Bonus", required=True, default=0, digits=dp.get_precision('Contract') )
    ni_price_adjustment_penalty = fields.Float( string="Nickel Price Adjustment Penalty", required=True, default=0, digits=dp.get_precision('Contract') )
    ni_price_adjustment_level = fields.Float( string="Nickel Price Adjustment Bonus Levels", required=True, default=0, digits=dp.get_precision('Contract') )

    use_rejection = fields.Boolean( string="Use Rejection", default=False )
    ni_rejection_spec = fields.Float( string="Rejection Specification (%)", required=True, default=0, digits=dp.get_precision('Contract') )
    ni_price_adjustment_rejection = fields.Float( string="Price Adjustment", required=True, default=0, digits=dp.get_precision('Contract') )
    ni_price_adjustment_rejection_level = fields.Float( string="Price Adjustment Levels (%)", required=True, default=0, digits=dp.get_precision('Contract') )

    fe_spec_from = fields.Float( string="From", required=True, default=0, digits=dp.get_precision('Contract') )
    fe_spec_to = fields.Float( string="To", required=True, default=0, digits=dp.get_precision('Contract') )
    fe_price_adjustment_bonus = fields.Float( string="Fe Price Adjustment Bonus", required=True, default=0, digits=dp.get_precision('Contract') )
    fe_price_adjustment_penalty = fields.Float( string="Fe Price Adjustment Penalty", required=True, default=0, digits=dp.get_precision('Contract') )
    fe_price_adjustment_level = fields.Float( string="Fe Price Adjustment Levels", required=True, default=0, digits=dp.get_precision('Contract') )

    moisture_spec_from = fields.Float( string="From", required=True, default=0, digits=dp.get_precision('Contract') )
    moisture_spec_to = fields.Float( string="To", required=True, default=0, digits=dp.get_precision('Contract') )
    moisture_price_adjustment_bonus = fields.Float( string="Moisture Price Adjustment Bonus", required=True, default=0, digits=dp.get_precision('Contract') )
    moisture_price_adjustment_penalty = fields.Float( string="Moisture Price Adjustment Penalty", required=True, default=0, digits=dp.get_precision('Contract') )
    moisture_price_adjustment_level = fields.Float( string="Moisture Price Adjustment Levels", required=True, default=0, digits=dp.get_precision('Contract') )
    
    mineral_spec_from = fields.Float( string="From", required=True, default=0, digits=dp.get_precision('Contract') )
    mineral_spec_to = fields.Float( string="To", required=True, default=0, digits=dp.get_precision('Contract') )
    
    progress = fields.Float( string="Progress", readonly=True, default=0, compute="_set_progress" )

    state = fields.Selection([
        ('open', 'In Progress'),
        ('closed', 'Terminated')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

    _constraints = [ 
        (_cek_fe, 'Spesifikasi Fe Tidak Valid', ['fe_spec_from','fe_spec_to'] ) ,
        (_cek_moisture, 'Spesifikasi Moisture Tidak Valid', ['moisture_spec_from','moisture_spec_to'] ),
        (_cek_mineral, 'Spesifikasi SiO2/MgO Tidak Valid', ['mineral_spec_from','mineral_spec_to'] )
        ]
    
    @api.depends("end_date")
    def _set_is_expired(self):
        for rec in self:
            end_date = datetime.strptime(rec.end_date, '%Y-%m-%d')
            rec.is_expired = datetime.today() > end_date

    @api.depends("quantity")
    def _set_progress(self):
        for rec in self:
            ShippingSudo = self.env['shipping.shipping'].sudo()
            shipping_ids = ShippingSudo.search([ ("sale_contract_id", '=', rec.id ) ])
            shipping_quantity = sum([ shipping.quantity for shipping in shipping_ids ])
            rec.quantity = rec.quantity if rec.quantity else 1.0
            rec.progress = shipping_quantity /rec.quantity * 100

    @api.multi
    def contract_open(self):
        for record in self:
            record.state = 'open'

    @api.multi
    def contract_close(self):
        for record in self:
            record.state = 'closed'

    @api.multi
    def act_renew_contract(self):
        assert len(self.ids) == 1, "This operation should only be done for 1 single contract at a time, as it it suppose to open a window as result"
        for element in self:
            #compute end date
            # startdate = fields.Date.from_string(element.start_date)
            # enddate = fields.Date.from_string(element.expiration_date)
            # diffdate = (enddate - startdate)
            default = {
                'name': element.name + "(RENEW)",
            }
            newid = element.copy(default).id
            element.contract_close( )
        return {
            'name': _("Renew Contract"),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_contract.view_sale_contract_form').id,
            'view_type': 'tree,form',
            'res_model': 'sale.contract',
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'res_id': newid,
            'context': {'active_id': newid},
        }