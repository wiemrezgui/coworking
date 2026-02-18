from odoo import models, fields

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
    status = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='available')
    borrower_id = fields.Many2one('res.partner', string='Borrower')
    borrow_date = fields.Datetime(string='Borrow Date')
    notes = fields.Text(string='Notes')
    def action_borrow(self):
        self.status = 'borrowed'

    def action_return(self):
        self.status = 'available'
        self.borrower_id = False
        self.borrow_date = False

    def action_maintenance(self):
        self.status = 'maintenance'

    def action_available(self):
        self.status = 'available'