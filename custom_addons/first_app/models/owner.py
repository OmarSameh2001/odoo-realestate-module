from odoo import models , fields, api

# Kept model and saved in database, it represents the business object
class Owner(models.Model):
    _name = 'owner'

    name = fields.Char(string='Property Name', required=True)
    address = fields.Text(string='Description')
    phone = fields.Char(string='Phone', required=True)
    property_ids = fields.One2many('property', 'owner_id', string='Properties')

    @api.constrains('phone')
    def _check_price(self):
        for rec in self:
         if len(rec.phone) < 11:
            raise models.ValidationError('The phone number must be at least 11 characters')


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique'),
    ]