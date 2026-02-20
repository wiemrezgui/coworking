from odoo import models, fields, api
from odoo.exceptions import ValidationError
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
    
    duration_value = fields.Float(string='Duration', default=1.0, required=True)
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
        """Calcule la date de fin en fonction du type et de la durée"""
        for booking in self:
            if booking.start_date and booking.duration_value:
                if booking.booking_type == 'hourly':
                    booking.end_date = booking.start_date + timedelta(hours=booking.duration_value)
                elif booking.booking_type == 'daily':
                    booking.end_date = booking.start_date + timedelta(days=booking.duration_value)
                elif booking.booking_type == 'monthly':
                    booking.end_date = booking.start_date + timedelta(days=30 * booking.duration_value)

    @api.depends('space_id', 'booking_type', 'duration_value')
    def _compute_total_price(self):
        """Calcule le prix total"""
        for booking in self:
            if booking.space_id and booking.duration_value:
                if booking.booking_type == 'hourly':
                    booking.total_price = booking.duration_value * booking.space_id.hourly_rate
                elif booking.booking_type == 'daily':
                    booking.total_price = booking.duration_value * booking.space_id.daily_rate
                elif booking.booking_type == 'monthly':
                    booking.total_price = booking.duration_value * booking.space_id.monthly_rate

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for booking in self:
            if booking.start_date and booking.end_date:
                if booking.start_date >= booking.end_date:
                    raise ValidationError(" End date must be strictly after start date.")
                
                # Vérifier que la réservation n'est pas trop dans le passé
                if booking.start_date < datetime.now() - timedelta(days=1):
                    raise ValidationError(" Cannot book dates in the past.")

    @api.constrains('duration_value')
    def _check_duration(self):
        """Vérifie que la durée est valide selon le type"""
        for booking in self:
            if booking.duration_value <= 0:
                raise ValidationError(" Duration must be greater than 0.")
            
            if booking.booking_type == 'hourly':
                if booking.duration_value > 168:  # 7 jours max en heures
                    raise ValidationError(" Maximum 168 hours (7 days) per hourly booking.")
                if booking.duration_value < 0.5:
                    raise ValidationError(" Minimum 30 minutes for hourly booking.")
                    
            elif booking.booking_type == 'daily':
                if booking.duration_value > 90:
                    raise ValidationError(" Maximum 90 days per daily booking.")
                if booking.duration_value < 0.5:
                    raise ValidationError(" Minimum half day (0.5) for daily booking.")
                    
            elif booking.booking_type == 'monthly':
                if booking.duration_value > 24:
                    raise ValidationError(" Maximum 24 months per monthly booking.")
                if booking.duration_value < 0.5:
                    raise ValidationError(" Minimum half month (0.5) for monthly booking.")

    @api.constrains('space_id', 'start_date', 'end_date')
    def _check_availability(self):
        """Vérifie que l'espace n'est pas déjà réservé"""
        for booking in self:
            if booking.space_id and booking.start_date and booking.end_date:
                overlapping = self.search([
                    ('space_id', '=', booking.space_id.id),
                    ('id', '!=', booking.id),
                    ('status', 'not in', ['cancelled']),
                    ('start_date', '<', booking.end_date),
                    ('end_date', '>', booking.start_date)
                ])
                if overlapping:
                    raise ValidationError(
                        f" Space '{booking.space_id.name}' is already booked for this period."
                    )

    def action_confirm(self):
        """Confirme la réservation et ferme le formulaire"""
        self.status = 'confirmed'
        
        # Notification
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Booking Confirmed',
                'message': f'Booking for {self.space_id.name} confirmed',
                'sticky': False,
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window_close',  # Ferme le formulaire
                }
            }
        }
        
        # Après la notification, on veut fermer le formulaire
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Booking Confirmed',
                'message': f'Booking for {self.space_id.name} confirmed',
                'sticky': False,
                'type': 'success',
            }
        }

    def action_cancel(self):
        """Annule la réservation"""
        self.status = 'cancelled'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Booking Cancelled',
                'message': 'Booking has been cancelled',
                'sticky': False,
                'type': 'warning',
            }
        }

    def action_complete(self):
        """Marque la réservation comme terminée"""
        self.status = 'completed'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Booking Completed',
                'message': 'Booking marked as completed',
                'sticky': False,
                'type': 'success',
            }
        }

    @api.onchange('booking_type')
    def _onchange_booking_type(self):
        """Affiche des instructions selon le type de réservation"""
        if self.booking_type:
            self.duration_value = 1.0
            
            messages = {
                'hourly': {
                    'title': ' Réservation horaire',
                    'msg': "• Entrez le nombre d'heures (min 0.5h, max 168h)\n• Exemples: 1, 2, 1.5 (1h30), 0.5 (30min)"
                },
                'daily': {
                    'title': ' Réservation journalière',
                    'msg': "• Entrez le nombre de jours (min 0.5j, max 90j)\n• Exemples: 1, 3, 0.5 (demi-journée), 7 (1 semaine)"
                },
                'monthly': {
                    'title': ' Réservation mensuelle',
                    'msg': "• Entrez le nombre de mois (min 0.5 mois, max 24 mois)\n• Exemples: 1, 3, 6, 12 (1 an), 1.5 (1 mois et demi)"
                }
            }
            
            info = messages.get(self.booking_type)
            if info:
                return {
                    'warning': {
                        'title': info['title'],
                        'message': f"{info['msg']}\n\n Le prix total sera calculé automatiquement"
                    }
                }