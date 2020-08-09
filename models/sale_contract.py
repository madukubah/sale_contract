from odoo import api, exceptions, fields, models, _
import time


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
    park_industry_id	= fields.Many2one('sale.park.industry', related="factory_id.park_industry_id", string='Park Industry', readonly=True,  ondelete="restrict" )

    start_date = fields.Date('Start Date', help='',  default=time.strftime("%Y-%m-%d") )
    end_date = fields.Date('End Date', help='',  default=time.strftime("%Y-%m-%d") )

    base_price = fields.Float( string="Base Price", required=True, default=0, digits=0 )
    ni_price_adjustment_bonus = fields.Float( string="Nickel Price Adjustment Bonus", required=True, default=0, digits=0 )
    ni_price_adjustment_penalty = fields.Float( string="Nickel Price Adjustment Penalty", required=True, default=0, digits=0 )

    fe_price_adjustment_bonus = fields.Float( string="Fe Price Adjustment Bonus", required=True, default=0, digits=0 )
    fe_price_adjustment_penalty = fields.Float( string="Fe Price Adjustment Penalty", required=True, default=0, digits=0 )

    moisture_price_adjustment_bonus = fields.Float( string="Moisture Price Adjustment Bonus", required=True, default=0, digits=0 )
    moisture_price_adjustment_penalty = fields.Float( string="Moisture Price Adjustment Penalty", required=True, default=0, digits=0 )

    quantity = fields.Float( string="Quantity (WMT)", required=True, default=0, digits=0 )

    ni_spec = fields.Float( string="Ni Specification (%)", required=True, default=0, digits=0 )
    fe_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    fe_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )
    moisture_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    moisture_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )
    mineral_spec_from = fields.Float( string="From", required=True, default=0, digits=0 )
    mineral_spec_to = fields.Float( string="To", required=True, default=0, digits=0 )

    state = fields.Selection([
        ('open', 'In Progress'),
        ('closed', 'Terminated')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

    _constraints = [ 
        (_cek_fe, 'Spesifikasi Fe Tidak Valid', ['fe_spec_from','fe_spec_to'] ) ,
        (_cek_moisture, 'Spesifikasi Moisture Tidak Valid', ['moisture_spec_from','moisture_spec_to'] ),
        (_cek_mineral, 'Spesifikasi SiO2/MgO Tidak Valid', ['mineral_spec_from','mineral_spec_to'] )
        ]

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
                # 'date': fields.Date.context_today(self),
                # 'start_date': fields.Date.to_string(fields.Date.from_string(element.expiration_date) + relativedelta(days=1)),
                # 'expiration_date': fields.Date.to_string(enddate + diffdate),
                'name': element.name + "(RENEW)",
            }
            newid = element.copy(default).id
            # newid = element.copy( ).id
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