from odoo import api, exceptions, fields, models, _
import time
from datetime import datetime
from odoo.addons import decimal_precision as dp

class SaleContract(models.Model):
    _name = "sale.contract"
    _order = "id desc"

    name = fields.Char(string="Name", size=100 , required=True)
    factory_id	= fields.Many2one('res.partner', string='Factory', required=True, domain=[ ('park_industry_id','!=',False)], ondelete="restrict" )
    park_industry_id = fields.Many2one('sale.park.industry', related="factory_id.park_industry_id", string='Park Industry', readonly=True,  ondelete="restrict" )

    start_date = fields.Date('Start Date', help='',  default=time.strftime("%Y-%m-%d") )
    end_date = fields.Date('End Date', help='',  default=time.strftime("%Y-%m-%d") )
    is_expired = fields.Boolean( string="Progress", readonly=True, default=False, compute="_set_is_expired" )
    quantity = fields.Float( string="Quantity (WMT)", required=True, default=0, digits=0 )

    base_price = fields.Float( string="Base Price (USD)", required=True, default=0, digits=0 )

    specifications = fields.One2many(
        'sale.contract.element.spec',
        'sale_contract_id',
        string='Specifications',
        copy=True )

    progress = fields.Float( string="Progress", readonly=True, default=0, compute="_set_progress" )

    state = fields.Selection([
        ('open', 'In Progress'),
        ('closed', 'Terminated')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

    @api.depends("end_date")
    def _set_is_expired(self):
        for record in self:
            end_date = datetime.strptime(record.end_date, '%Y-%m-%d')
            record.is_expired = datetime.today() > end_date

    @api.depends("quantity")
    def _set_progress(self):
        for record in self:
            ShippingSudo = self.env['shipping.order'].sudo()
            shipping_ids = ShippingSudo.search([ ("sale_contract_id", '=', record.id ) ])
            shipping_quantity = sum([ shipping.quantity for shipping in shipping_ids ])
            record.quantity = record.quantity if record.quantity else 1.0
            record.progress = shipping_quantity /record.quantity * 100

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