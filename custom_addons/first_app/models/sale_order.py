from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    property_id = fields.Many2one('property', string='Property')