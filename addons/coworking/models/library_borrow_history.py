from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryBorrowHistory(models.Model):
    _name = 'library.borrow.history'
    _description = 'Library Borrow History'
    _order = 'borrow_date desc'

    item_id = fields.Many2one('library.item', string='Item', required=True, ondelete='cascade')
    borrower_id = fields.Many2one('coworking.customer', string='Borrower', required=True)
    borrow_date = fields.Datetime(string='Borrow Date', required=True, default=fields.Datetime.now)
    return_date = fields.Datetime(string='Return Date')
    
    @api.constrains('item_id', 'return_date')
    def _check_borrow_limit(self):
        """Vérifie qu'on ne dépasse pas la quantité disponible"""
        for record in self:
            if not record.return_date:  # Seulement pour les nouveaux emprunts
                item = record.item_id
                # Compter les emprunts en cours (sans date de retour)
                current_borrows = self.search_count([
                    ('item_id', '=', item.id),
                    ('return_date', '=', False),
                    ('id', '!=', record.id)
                ])
                if current_borrows >= item.total_quantity:
                    raise ValidationError(
                        f"Cannot borrow {item.name}: All items are already borrowed "
                        f"({item.total_quantity} total, {current_borrows} borrowed)."
                    )
    
    @api.model
    def create(self, vals):
        """Surcharge de la création pour gérer la disponibilité"""
        # Vérifier la disponibilité avant création
        if 'item_id' in vals and 'return_date' not in vals:
            item = self.env['library.item'].browse(vals['item_id'])
            
            # Compter les emprunts en cours
            current_borrows = self.search_count([
                ('item_id', '=', item.id),
                ('return_date', '=', False)
            ])
            
            if current_borrows >= item.total_quantity:
                raise ValidationError(
                    f"Cannot borrow {item.name}: No items available. "
                    f"({current_borrows}/{item.total_quantity} already borrowed)"
                )
        
        # Créer l'emprunt
        res = super(LibraryBorrowHistory, self).create(vals)
        res.item_id.invalidate_recordset(['borrow_history_ids'])
        return res
    
    def write(self, vals):
        res = super(LibraryBorrowHistory, self).write(vals)
        if 'return_date' in vals:
            items = self.mapped('item_id')
            items.invalidate_recordset(['borrow_history_ids'])
        return res
    
    def unlink(self):
        """Empêcher la suppression des emprunts avec retour"""
        for record in self:
            if record.return_date:
                raise ValidationError(
                    "Cannot delete a borrow history that already has a return date. "
                    "You can only delete active borrows."
                )
        items = self.mapped('item_id')
        res = super(LibraryBorrowHistory, self).unlink()
        
        # Forcer le recalcul pour les items concernés
        for item in items:
            item._compute_quantities()
            item._compute_status()
        
        return res
    
    def action_return_selected(self):
        """Action pour retourner les items sélectionnés"""
        for record in self:
            if not record.return_date:
                record.return_date = fields.Datetime.now()
        
        # Message de confirmation groupé
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Items Returned',
                'message': f"{len(self)} item(s) returned successfully",
                'sticky': False,
                'type': 'success',
            }
        }
    
    def action_borrow_multiple(self):
        """Action pour emprunter plusieurs items à la fois"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Borrow Items',
            'res_model': 'library.borrow.history',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_borrow_date': fields.Datetime.now(),
            }
        }
    
    @api.model
    def get_availability_info(self, item_id):
        """Retourne les informations de disponibilité pour un item"""
        item = self.env['library.item'].browse(item_id)
        current_borrows = self.search_count([
            ('item_id', '=', item_id),
            ('return_date', '=', False)
        ])
        
        return {
            'item_name': item.name,
            'total': item.total_quantity,
            'borrowed': current_borrows,
            'available': item.total_quantity - current_borrows,
            'status': item.status,
        }
    
    @api.model
    def get_borrow_stats(self):
        """Statistiques globales des emprunts"""
        total_borrows = self.search_count([])
        active_borrows = self.search_count([('return_date', '=', False)])
        returned = self.search_count([('return_date', '!=', False)])
        
        return {
            'total_borrows': total_borrows,
            'active_borrows': active_borrows,
            'returned': returned,
        }