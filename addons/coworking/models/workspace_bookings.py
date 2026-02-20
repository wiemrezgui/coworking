from odoo import models, fields, api
from datetime import datetime, timedelta

class WorkspaceBooking(models.Model):
    _name = 'workspace.booking'
    _description = 'Workspace Booking'
    _order = 'start_date desc'

    space_id = fields.Many2one('workspace.space', string='Space', required=True)
    customer_id = fields.Many2one('coworking.customer', string='Customer', required=True)
    booking_type = fields.Selection([
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly')
    ], string='Booking Type', required=True)
    
    # Champs pour la durée
    duration_value = fields.Float(string='Duration', default=1.0, required=True)
    
    # Dates calculées
    start_date = fields.Datetime(string='Start Date', required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date', compute='_compute_end_date', store=True, readonly=False)
    
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], string='Status', default='pending')
    notes = fields.Text(string='Notes')
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)

    @api.depends('booking_type', 'duration_value', 'start_date')
    def _compute_end_date(self):
        for booking in self:
            if booking.start_date and booking.duration_value:
                if booking.booking_type == 'hourly':
                    booking.end_date = booking.start_date + timedelta(hours=booking.duration_value)
                elif booking.booking_type == 'daily':
                    booking.end_date = booking.start_date + timedelta(days=booking.duration_value)
                elif booking.booking_type == 'monthly':
                    # Approximation: 30 jours par mois
                    booking.end_date = booking.start_date + timedelta(days=30 * booking.duration_value)

    @api.depends('space_id', 'booking_type', 'duration_value')
    def _compute_total_price(self):
        for booking in self:
            if booking.space_id and booking.duration_value:
                if booking.booking_type == 'hourly':
                    booking.total_price = booking.duration_value * booking.space_id.hourly_rate
                elif booking.booking_type == 'daily':
                    booking.total_price = booking.duration_value * booking.space_id.daily_rate
                elif booking.booking_type == 'monthly':
                    booking.total_price = booking.duration_value * booking.space_id.monthly_rate

    def action_confirm(self):
        self.status = 'confirmed'

    def action_cancel(self):
        self.status = 'cancelled'

    def action_complete(self):
        self.status = 'completed'
    @api.onchange('booking_type')

    def _onchange_booking_type(self):
        if self.booking_type:
            if self.booking_type == 'hourly':
                self.duration_value = 1.0
            elif self.booking_type == 'daily':
                self.duration_value = 1.0
            elif self.booking_type == 'monthly':
                self.duration_value = 1.0
            # Ajuster le libellé dans l'interface
            return {
                'warning': {
                    'title': 'Information',
                    'message': f'Entrez le nombre de {self.booking_type} dans le champ "Duration"'
                }
            }