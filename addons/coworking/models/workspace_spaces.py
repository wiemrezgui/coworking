from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WorkspaceSpace(models.Model):
    _name = 'workspace.space'
    _description = 'Workspace Space'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    space_type_id = fields.Many2one('workspace.type', string='Space Type', required=True)
    location_floor = fields.Char(string='Floor')
    location_zone = fields.Char(string='Zone')
    capacity = fields.Integer(string='Capacity', required=True)
    hourly_rate = fields.Float(string='Hourly Rate', digits=(16, 2))
    daily_rate = fields.Float(string='Daily Rate', digits=(16, 2))
    monthly_rate = fields.Float(string='Monthly Rate', digits=(16, 2))
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    photos = fields.Binary(string='Photos')
    amenity_ids = fields.Many2many(
        'workspace.amenity',
        'workspace_space_amenity_rel',
        'space_id',
        'amenity_id',
        string='Amenities'
    )

    @api.constrains('name')
    def _check_name(self):
        """Vérifie que le nom a au moins 2 caractères"""
        for space in self:
            if space.name and len(space.name.strip()) < 2:
                raise ValidationError(" Space name must be at least 2 characters long.")

    @api.constrains('capacity')
    def _check_capacity(self):
        """Vérifie que la capacité est valide"""
        for space in self:
            if space.capacity <= 0:
                raise ValidationError(" Capacity must be greater than 0.")
            if space.capacity > 500:
                raise ValidationError(" Capacity cannot exceed 500 people.")

    @api.constrains('hourly_rate', 'daily_rate', 'monthly_rate')
    def _check_rates(self):
        """Vérifie que les tarifs sont valides"""
        for space in self:
            if space.hourly_rate < 0:
                raise ValidationError(" Hourly rate cannot be negative.")
            if space.daily_rate < 0:
                raise ValidationError(" Daily rate cannot be negative.")
            if space.monthly_rate < 0:
                raise ValidationError(" Monthly rate cannot be negative.")
            
            # Vérifie la cohérence des prix (optionnel)
            if space.hourly_rate > 0 and space.daily_rate > 0:
                if space.daily_rate > space.hourly_rate * 24:
                    raise ValidationError(" Daily rate seems too high compared to hourly rate.")
            
            if space.daily_rate > 0 and space.monthly_rate > 0:
                if space.monthly_rate > space.daily_rate * 31:
                    raise ValidationError(" Monthly rate seems too high compared to daily rate.")

    @api.onchange('hourly_rate')
    def _onchange_hourly_rate(self):
        """Suggère des tarifs journalier et mensuel basés sur le tarif horaire"""
        if self.hourly_rate and self.hourly_rate > 0:
            if not self.daily_rate:
                self.daily_rate = self.hourly_rate * 8  # 8 heures = 1 jour
            if not self.monthly_rate:
                self.monthly_rate = self.hourly_rate * 8 * 22  # 22 jours ouvrés