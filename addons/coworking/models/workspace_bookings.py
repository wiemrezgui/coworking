from odoo import models, fields, api
from datetime import datetime

class WorkspaceBooking(models.Model):
    _name = 'workspace.booking'
    _description = 'Workspace Booking'
    _order = 'start_date desc'

    space_id = fields.Many2one('workspace.space', string='Space', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    booking_type = fields.Selection([
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly')
    ], string='Booking Type', required=True)
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], string='Status', default='pending')
    notes = fields.Text(string='Notes')
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)

    @api.depends('space_id', 'booking_type', 'start_date', 'end_date')
    def _compute_total_price(self):
        for booking in self:
            if booking.space_id and booking.start_date and booking.end_date:
                duration = (booking.end_date - booking.start_date).total_seconds() / 3600  # hours
                if booking.booking_type == 'hourly':
                    booking.total_price = duration * booking.space_id.hourly_rate
                elif booking.booking_type == 'daily':
                    days = duration / 24
                    booking.total_price = days * booking.space_id.daily_rate
                elif booking.booking_type == 'monthly':
                    months = duration / (24 * 30)  # approximate
                    booking.total_price = months * booking.space_id.monthly_rate