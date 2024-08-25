from email.policy import default
from dateutil.relativedelta import relativedelta
from docutils.nodes import warning
from odoo import models , fields, api
from odoo.tools.populate import compute


# Kept model and saved in database, it represents the business object
class Property(models.Model):
    _name = 'property'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Property Name', required=True, tracking=True)
    ref = fields.Char(string='Property Reference', default='New', readonly=True)
    description = fields.Text(string='Description')
    purchase_price = fields.Float(string='Purchase Price')
    sold_price = fields.Float(string='Sold Price', tracking=True)
    earning = fields.Float(compute='_compute_sale', string='Earning', store=True)
    margin = fields.Float(compute='_compute_sale', string='Margin', store=True)
    margin_percent = fields.Float(compute='_compute_sale', string='Margin')
    date_added = fields.Date(string='Date Added', default=fields.Date.today())
    date_selling_period = fields.Date(
        string='Selling Period',
        compute='_compute_date_selling_period',
        store=True
    )
    date_sold = fields.Date(string='Date Sold', compute='_compute_sale')
    is_late = fields.Boolean(compute='check_expected_selling_date', string='Is Selling Late', store=True)
    bedrooms = fields.Integer(string='Bedrooms Count', compute='_compute_bedrooms', default=0)
    bedroom_ids = fields.One2many('property.bedroom', 'property_id', string='Bedrooms', store=True)
    garden = fields.Boolean(string='Has Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], string='Garden Orientation', default='north')
    owner_id = fields.Many2one('owner', string='Owner', tracking=True)
    owner_phone = fields.Char(related='owner_id.phone', string='Owner Phone')
    owner_address = fields.Text(related='owner_id.address', string='Owner Address')
    state= fields.Selection([
        ('available', 'Available'),
        ('on_sale', 'On Sale'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
    ], string='State', tracking=True, default='available')
    active= fields.Boolean(string='Active', default=True)


    @api.depends('state')
    def _compute_date_selling_period(self):
        for rec in self:
            if rec.sold_price != 0 and rec.state != 'sold':
                raise models.ValidationError('The state cannot be non sold unless the sold price is 0')
            elif rec.state == 'on_sale' and rec.date_selling_period == False:
                rec.date_selling_period = fields.Date.today() + relativedelta(months=1)
            else:
                rec.date_selling_period = False

    @api.constrains('purchase_price', 'sold_price')
    def _check_price(self):
        if self.sold_price < 0 or self.purchase_price < 0:
            raise models.ValidationError('The price cannot be negative')

    @api.depends('sold_price', 'purchase_price', 'state')
    def _compute_sale(self):
        for rec in self:
            if rec.state != 'sold':
                rec.earning = rec.margin = rec.margin_percent = rec.date_sold = None
            # elif rec.sold_price <= 0 or rec.purchase_price <= 0:
            #     raise models.ValidationError('Please enter the sold and purchase prices')
            else:
                rec.earning = rec.sold_price - rec.purchase_price
                rec.margin = rec.earning / rec.purchase_price
                rec.margin_percent = rec.margin * 100
                rec.date_sold = fields.Date.today()



    @api.depends('bedroom_ids')
    def _compute_bedrooms(self):
        for rec in self:
            rec.bedrooms = len(rec.bedroom_ids)
    @api.onchange('garden')
    def _check_garden(self):
        for rec in self:
         if not rec.garden:
            rec.garden_area = 0
            rec.garden_orientation = 'north'

    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('property.ref')
        return res

    def function(self):
        action = self.env['ir.actions.actions']._for_xml_id('first_app.property_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action

    def check_expected_selling_date(self):
        property_ids = self.search([('date_selling_period', '<', fields.Date.today())])
        for rec in property_ids:
            if rec.date_selling_period and rec.date_selling_period < fields.Date.today() and (rec.state == 'on_sale' or rec.state == 'pending'):
                rec.is_late = True

    # def open_new_page(self):
    #     action = self.env['ir.actions.actions']._for_xml_id('first_app.owner_action')
    #     view_id = self.env.ref('first_app.owner_view_form').id
    #     action['views'] = [(view_id, 'form')]
    #     action['res_id'] = self.owner_id.id
    #     return action
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique'),
    ]


# super(Property, self).write(vals)
# self.env['property.bedroom'].create({'description': 'test', 'area': 10, 'orientation': 'north', 'balcony': True, 'property_id': 1})
# @api.model
    def write(self, vals):
        print(vals)
        super(Property, self).write(vals)
        return super(Property, self).write(vals)
# def _search(self, args, offset=0, limit=None, order=None, count=False):
#     return super(Property, self)._search(args, offset=offset, limit=limit, order=order, count=count)
# def _unlink(self):
#     return super(Property, self)._unlink()

class PropertyBedroom(models.Model):
    _name = 'property.bedroom'
    _description = 'Property Bedroom'

    description = fields.Text(string='Description')
    area = fields.Integer(string='Area')
    orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], string='Bedroom Orientation', default='north')
    balcony = fields.Boolean(string='Has Balcony')
    property_id = fields.Many2one('property', string='Property')