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
        ('fair', 'Fair')
    ], string='Condition', default='good')
    
    # Quantité totale
    total_quantity = fields.Integer(string='Total Quantity', default=1, required=True)
    
    # Seulement available_quantity (plus de borrowed_quantity)
    available_quantity = fields.Integer(string='Available Quantity', compute='_compute_quantities', search=True)
    
    status = fields.Selection([
        ('available', 'Available'),
        ('limited', 'Limited'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Maintenance'),
        ('unavailable', 'Unavailable')
    ], string='Status', compute='_compute_status', search=True, default='available')
    
    # Emprunteurs actuels
    current_borrower_ids = fields.One2many('library.borrow.history', 'item_id', 
                                           string='Current Borrowers',
                                           domain=[('return_date', '=', False)])
    
    notes = fields.Text(string='Notes')
    total_borrow_count = fields.Integer(string='Total Borrows', compute='_compute_total_borrow_count', search=True)
    borrow_history_ids = fields.One2many('library.borrow.history', 'item_id', string='Borrow History')
    
    @api.depends('total_quantity', 'borrow_history_ids.return_date')
    def _compute_quantities(self):
        """Calcule les quantités disponibles"""
        for item in self:
            borrowed = self.env['library.borrow.history'].search_count([
                ('item_id', '=', item.id),
                ('return_date', '=', False)
            ])
            item.available_quantity = item.total_quantity - borrowed
    
    @api.depends('available_quantity', 'total_quantity', 'condition')
    def _compute_status(self):
        """Calcule le statut en fonction des quantités"""
        for item in self:
            if item.condition == 'maintenance':
                item.status = 'maintenance'
            elif item.available_quantity <= 0:
                item.status = 'unavailable'
            elif item.available_quantity < item.total_quantity:
                item.status = 'limited'
            else:
                item.status = 'available'
    
    @api.depends('borrow_history_ids')
    def _compute_total_borrow_count(self):
        """Calcule le nombre total d'emprunts"""
        for item in self:
            item.total_borrow_count = self.env['library.borrow.history'].search_count([('item_id', '=', item.id)])

    @api.constrains('total_quantity')
    def _check_quantity(self):
        """Vérifie que la quantité totale est positive"""
        for item in self:
            if item.total_quantity <= 0:
                raise ValidationError("Total quantity must be greater than 0.")

    def action_borrow(self):
        """Action pour emprunter cet équipement"""
        self.ensure_one()
        if self.available_quantity <= 0:
            raise ValidationError(f"No items available to borrow for {self.name}.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Borrow {self.name}',
            'res_model': 'library.borrow.history',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_item_id': self.id,
                'default_borrow_date': fields.Datetime.now(),
            }
        }

    def action_return(self):
        """Action pour retourner un équipement"""
        self.ensure_one()
        active_borrow = self.env['library.borrow.history'].search([
            ('item_id', '=', self.id),
            ('return_date', '=', False)
        ], limit=1)
        
        if active_borrow:
            active_borrow.return_date = fields.Datetime.now()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Return Successful',
                    'message': f'{self.name} returned successfully',
                    'sticky': False,
                    'type': 'success',
                }
            }
        else:
            raise ValidationError(f"No active borrow found for {self.name}.")

    def action_maintenance(self):
        """Mettre en maintenance"""
        self.ensure_one()
        self.condition = 'maintenance'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Maintenance Mode',
                'message': f'{self.name} is now in maintenance',
                'sticky': False,
                'type': 'warning',
            }
        }

    def action_available(self):
        """Remettre disponible"""
        self.ensure_one()
        self.condition = 'good'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Available',
                'message': f'{self.name} is now available',
                'sticky': False,
                'type': 'success',
            }
        }