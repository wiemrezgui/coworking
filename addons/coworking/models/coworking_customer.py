from odoo import models, fields, api

class CoworkingCustomer(models.Model):
    _name = 'coworking.customer'
    _description = 'Coworking Customer'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    company = fields.Char(string='Company' , required=False)
    vat = fields.Char(string='VAT')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    
    # Relation avec les réservations
    booking_ids = fields.One2many('workspace.booking', 'customer_id', string='Bookings')
    
    # Relation avec les emprunts
    borrow_ids = fields.One2many('library.borrow.history', 'borrower_id', string='Borrows')
    
    # Pour compter les réservations
    booking_count = fields.Integer(string='Booking Count', compute='_compute_booking_count')
    
    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for customer in self:
            customer.booking_count = len(customer.booking_ids)