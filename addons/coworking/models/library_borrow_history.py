from odoo import models, fields

class LibraryBorrowHistory(models.Model):
    _name = 'library.borrow.history'
    _description = 'Library Borrow History'
    _order = 'borrow_date desc'

    item_id = fields.Many2one('library.item', string='Item', required=True)
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True)
    borrow_date = fields.Datetime(string='Borrow Date', required=True)
    return_date = fields.Datetime(string='Return Date')
