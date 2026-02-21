# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarEvent(models.Model):
    """Étendre le modèle calendar.event pour lier avec vos réservations"""
    _inherit = 'calendar.event'
    
    # Lien vers votre réservation
    booking_id = fields.Many2one('workspace.booking', string='Réservation', ondelete='cascade')


class WorkspaceBooking(models.Model):
    """Étendre votre modèle de réservation pour créer des événements dans le calendrier"""
    _inherit = 'workspace.booking'
    
    # Lien vers l'événement calendrier
    calendar_event_id = fields.Many2one('calendar.event', string='Événement Calendrier', copy=False)
    
    @api.model
    def create(self, vals):
        """Quand on crée une réservation, créer aussi un événement dans le calendrier si confirmée"""
        booking = super(WorkspaceBooking, self).create(vals)
        if booking.status == 'confirmed':
            booking._create_calendar_event()
        return booking
    
    def write(self, vals):
        """Quand on modifie une réservation, mettre à jour l'événement calendrier"""
        res = super(WorkspaceBooking, self).write(vals)
        
        # Si le statut devient 'confirmed' et qu'il n'y a pas encore d'événement
        if vals.get('status') == 'confirmed':
            for booking in self:
                if not booking.calendar_event_id:
                    booking._create_calendar_event()
        
        # Si la réservation est annulée, supprimer l'événement
        if vals.get('status') == 'cancelled':
            for booking in self:
                if booking.calendar_event_id:
                    booking.calendar_event_id.unlink()
                    booking.calendar_event_id = False
        
        # Si les dates changent, mettre à jour l'événement
        if 'start_date' in vals or 'end_date' in vals:
            for booking in self:
                if booking.calendar_event_id:
                    booking.calendar_event_id.write({
                        'start': booking.start_date,
                        'stop': booking.end_date,
                    })
        
        return res
    
    def _create_calendar_event(self):
        """Crée un événement dans le calendrier pour cette réservation"""
        self.ensure_one()
        if not self.calendar_event_id and self.space_id and self.start_date and self.end_date:
            event = self.env['calendar.event'].create({
                'name': f"{self.space_id.name} - {self.customer_id.name}",
                'start': self.start_date,
                'stop': self.end_date,
                'booking_id': self.id,
                'description': f"Réservation pour {self.customer_id.name}\n"
                              f"Type: {self.booking_type}\n"
                              f"Durée: {self.duration_value}\n"
                              f"Prix: {self.total_price} DT",
                'location': f"Étage {self.space_id.location_floor}, Zone {self.space_id.location_zone}",
            })
            self.calendar_event_id = event.id
        return self.calendar_event_id
    
    def action_view_in_calendar(self):
        """Voir cette réservation dans le calendrier"""
        self.ensure_one()
        if self.calendar_event_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Calendrier',
                'res_model': 'calendar.event',
                'view_mode': 'form',
                'res_id': self.calendar_event_id.id,
                'target': 'current',
            }
        return True
    
    @api.model
    def sync_existing_bookings(self):
        """Synchroniser toutes les réservations existantes dans le calendrier"""
        bookings = self.search([('status', '=', 'confirmed'), ('calendar_event_id', '=', False)])
        count = 0
        for booking in bookings:
            if booking._create_calendar_event():
                count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Synchronisation',
                'message': f'{count} réservations ont été ajoutées au calendrier',
                'sticky': False,
                'type': 'success',
            }
        }