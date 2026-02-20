from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryItem(models.Model):
    _name = 'library.item'
    _description = 'Library Item'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    category = fields.Selection([
        ('monitor', 'Monitor'),
        ('cable', 'Cable'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('charger', 'Charger'),
        ('webcam', 'Webcam')
    ], string='Category', required=True)
    condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('maintenance', 'Maintenance')
    ], string='Condition', default='good')

    total_quantity = fields.Integer(string='Total Quantity', default=1, required=True)
    available_quantity = fields.Integer(string='Available Quantity', default=1, required=True)

    status = fields.Selection([
        ('available', 'Available'),
        ('limited', 'Limited'),
        ('unavailable', 'Unavailable'),
        ('maintenance', 'Maintenance'),
    ], string='Status', compute='_compute_status', store=True)

    notes = fields.Text(string='Notes')

    @api.depends('available_quantity', 'total_quantity', 'condition')
    def _compute_status(self):
        for item in self:
            if item.condition == 'maintenance':
                item.status = 'maintenance'
            elif item.available_quantity <= 0:
                item.status = 'unavailable'
            elif item.available_quantity < item.total_quantity:
                item.status = 'limited'
            else:
                item.status = 'available'

    @api.constrains('total_quantity', 'available_quantity')
    def _check_quantity(self):
        for item in self:
            if item.total_quantity <= 0:
                raise ValidationError("Total quantity must be greater than 0.")
            if item.available_quantity < 0:
                raise ValidationError("Available quantity cannot be negative.")
            if item.available_quantity > item.total_quantity:
                raise ValidationError("Available quantity cannot exceed total quantity.")

    def action_maintenance(self):
        self.ensure_one()
        self.condition = 'maintenance'

    def action_available(self):
        self.ensure_one()
        self.condition = 'good'