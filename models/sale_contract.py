from odoo import api, exceptions, fields, models, _
import time
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger( __name__ )

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

    hma_price = fields.Float( string="HMA Price (USD)", required=True, default=0, digits=0 )
    shipping_price = fields.Float( string="Shipping Cost", required=True, default=0, digits=0 )
    corrective_factor = fields.Float( string="Corrective Factor (%)", required=True, default=0, digits=0 )

    # XX = fields.Float( string="XX", required=True, default=0, digits=0, compute="compute_XX" )

    # base_price_select = fields.Selection([
    #     ('fix', 'Fixed Amount'),
    #     ('code', 'Python Code'),
    # ], string='Base Price Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
    # base_price = fields.Float( string="Base Price (USD)", required=True, default=0, digits=0 )
    # base_price_python_compute = fields.Text(string='Python Code',
    #     default='''
    #                 # Available variables:
    #                 #----------------------
    #                 # qaqc_coa: qaqc.coa.order object
    #                 # sale_contract: sale.contract object
    #                 # base_price_components: sale.contract.base.price.component object
    #                 result = 0''')

    base_price_components = fields.One2many(
        'sale.contract.base.price.component',
        'sale_contract_id',
        string='Base Price',
        copy=True )

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
    
    # def compute_XX(self):
        # self.XX = 100
        # self.XX = self.get_base_price_amount( 1 , self.id)

    @api.model
    def get_base_price_amount(self, qaqc_coa_id, contract_id, hma_price = 0 ):

        class BrowsableObject(object):
            def __init__(self, dict, env):
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0
        qaqc_coa = self.env['qaqc.coa.order'].browse( qaqc_coa_id )
        sale_contract = self.env['sale.contract'].browse( contract_id )
        base_price_component = self.env['sale.contract.base.price.component'].search( [( 'sale_contract_id', '=', contract_id )] )
        qaqc_coas = BrowsableObject(qaqc_coa, self.env)
        sale_contracts = BrowsableObject(sale_contract, self.env)
        base_price_components = BrowsableObject(base_price_component, self.env)
        for base_price_component in base_price_components.dict :
            _logger.warning( base_price_component )
        baselocaldict = {
            'qaqc_coa': qaqc_coas, 
            'sale_contract': sale_contracts, 
            'base_price_components': base_price_components, 
            'hma_price': hma_price, 
        }

        return self.compute_base_price(baselocaldict)
    
    def compute_base_price(self, localdict):
        self.ensure_one()
        base_price_components = localdict['base_price_components']
        qaqc_coa = localdict['qaqc_coa']
        sale_contract = self
        price_component_dict = {
            'main':[],
            'add':[],
            'subtract':[],
        }
        for base_price_component in base_price_components.dict :
            if price_component_dict.get( base_price_component.rule, False):
                price_component_dict[ base_price_component.rule ] += [ base_price_component ]
            else:
                price_component_dict[ base_price_component.rule ] = []
                price_component_dict[ base_price_component.rule ] += [ base_price_component ]

        # hma = sale_contract.hma_price
        hma = localdict['hma_price']
        shipping_price = sale_contract.shipping_price
        corrective_factor = sale_contract.corrective_factor

        hpm_price = 0
        if price_component_dict[ 'main' ] :
            main = price_component_dict[ 'main' ][0]
            main_spec_qaqc = 0
            for element_spec in qaqc_coa.dict.element_specs :
                if element_spec.element_id.id == main.element_id.id :
                    main_spec_qaqc = element_spec.spec
            diff = main_spec_qaqc - main.spec
            corrective_factor = corrective_factor + ( diff * 10 ) 
            hpm_price = hma * ( corrective_factor/100 ) * ( main_spec_qaqc/100 )

            hpm_price_temp = hpm_price
            for component_add in price_component_dict[ 'add' ] :
                for element_spec in qaqc_coa.dict.element_specs :
                    if element_spec.element_id.id == component_add.element_id.id :
                        hpm_price += hpm_price_temp * (element_spec.spec / 100)

            for component_subtract in price_component_dict[ 'subtract' ] :
                for element_spec in qaqc_coa.dict.element_specs :
                    if element_spec.element_id.id == component_subtract.element_id.id :
                        hpm_price -= hpm_price_temp * (element_spec.spec / 100)

        result = hpm_price + shipping_price
        return result
    #TODO should add some checks on the type of result (should be float)
    # @api.multi
    # def compute_base_price(self, localdict):
    #     """
    #     :param localdict: dictionary containing the environement in which to compute the rule
    #     :return: returns a tuple build as the base/amount computed, the quantity and the rate
    #     :rtype: (float, float, float)
    #     """
    #     self.ensure_one()
    #     if self.base_price_select == 'fix':
    #         try:
    #             return self.base_price
    #         except:
    #             raise UserError(_('Wrong quantity defined for contract %s .') % (self.name))
    #     else:
    #         try:
    #             safe_eval(self.base_price_python_compute, localdict, mode='exec', nocopy=True)
    #             return float(localdict['result'])
    #         except:
    #             raise UserError(_('Wrong python code defined for contract %s .') % (self.name))