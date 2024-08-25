from odoo import models, fields, api

class PropertyWizard(models.TransientModel):
    _name = 'property.wizard'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    purchase_price = fields.Float(string='Purchase Price', required=True)
    sold_price = fields.Float(string='Sold Price', required=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('on_sale', 'On Sale'),
        ('pending', 'Pending'),
        ('sold', 'Sold')
    ], string='State', required=True)
    property_id = fields.Many2one('property', string='Property')

    @api.onchange('property_id', 'name', 'description')
    def _onchange_property_id(self):
        if self.property_id:
            self.name = self.property_id.name
            self.description = self.property_id.description
            self.purchase_price = self.property_id.purchase_price
            self.sold_price = self.property_id.sold_price
            self.state = self.property_id.state
        else:
            self.name = False
            self.description = False
            self.purchase_price = False
            self.sold_price = False
            self.state = False

    @api.constrains('sold_price', 'purchase_price', 'state')
    def _check_error(self):
        if self.state == 'sold' and (self.sold_price <= 0 or self.purchase_price <= 0):
            raise models.ValidationError('The prices of sold property cannot be zero or negative')

    def confirm_state_wizard(self):
        self.property_id.write({
            'purchase_price': self.purchase_price,
            'sold_price': self.sold_price,
            'state': self.state
        })
        return {'type': 'ir.actions.act_window_close'}
