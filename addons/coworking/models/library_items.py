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
            elif item.available_quantity <= item.total_quantity*0.5:
                item.status = 'limited'
            else:
                item.status = 'available'

    @api.constrains('name')
    def _check_name(self):
        """Vérifie que le nom a au moins 2 caractères"""
        for item in self:
            if not item.name or len(item.name.strip()) < 2:
                raise ValidationError(" Le nom de l'équipement doit contenir au moins 2 caractères.")

    @api.constrains('total_quantity')
    def _check_total_quantity(self):
        """Vérifie que la quantité totale est valide"""
        for item in self:
            if item.total_quantity <= 0:
                raise ValidationError(" La quantité totale doit être supérieure à 0.")
            if item.total_quantity > 9999:
                raise ValidationError(" La quantité totale ne peut pas dépasser 9999.")

    @api.constrains('available_quantity')
    def _check_available_quantity(self):
        """Vérifie que la quantité disponible est valide"""
        for item in self:
            if item.available_quantity < 0:
                raise ValidationError(" La quantité disponible ne peut pas être négative.")
            if item.available_quantity > item.total_quantity:
                raise ValidationError(" La quantité disponible ne peut pas dépasser la quantité totale.")

    @api.constrains('category')
    def _check_category(self):
        """Vérifie que la catégorie est sélectionnée"""
        for item in self:
            if not item.category:
                raise ValidationError(" Veuillez sélectionner une catégorie.")

    @api.constrains('condition')
    def _check_condition(self):
        """Vérifie que l'état est valide"""
        valid_conditions = ['new', 'good', 'fair', 'maintenance']
        for item in self:
            if item.condition and item.condition not in valid_conditions:
                raise ValidationError(" L'état sélectionné n'est pas valide.")

    @api.onchange('total_quantity')
    def _onchange_total_quantity(self):
        """Ajuste automatiquement la quantité disponible si nécessaire"""
        if self.total_quantity and self.available_quantity > self.total_quantity:
            self.available_quantity = self.total_quantity
            return {
                'warning': {
                    'title': 'Ajustement automatique',
                    'message': 'La quantité disponible a été ajustée à la quantité totale.'
                }
            }

    @api.onchange('available_quantity')
    def _onchange_available_quantity(self):
        """Vérifie la quantité disponible en temps réel"""
        if self.total_quantity and self.available_quantity > self.total_quantity:
            return {
                'warning': {
                    'title': 'Attention',
                    'message': 'La quantité disponible ne peut pas dépasser la quantité totale.'
                }
            }
        if self.available_quantity < 0:
            return {
                'warning': {
                    'title': 'Attention',
                    'message': 'La quantité disponible ne peut pas être négative.'
                }
            }

    def action_maintenance(self):
        """Met l'équipement en maintenance"""
        self.ensure_one()
        self.condition = 'maintenance'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Mode Maintenance',
                'message': f"{self.name} est maintenant en maintenance",
                'sticky': False,
                'type': 'warning',
            }
        }

    def action_available(self):
        """Remet l'équipement disponible"""
        self.ensure_one()
        self.condition = 'good'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Disponible',
                'message': f"{self.name} est maintenant disponible",
                'sticky': False,
                'type': 'success',
            }
        }

    def action_check_availability(self):
        """Vérifie et affiche la disponibilité actuelle"""
        self.ensure_one()
        if self.available_quantity > 0:
            message = f"{self.available_quantity} sur {self.total_quantity} disponible(s)"
            if self.available_quantity == self.total_quantity:
                message = f"Tous les {self.total_quantity} équipements sont disponibles"
            elif self.available_quantity == 0:
                message = f"Aucun équipement disponible sur {self.total_quantity}"
        else:
            message = "Aucun équipement disponible"
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Disponibilité',
                'message': message,
                'sticky': False,
                'type': 'info',
            }
        }