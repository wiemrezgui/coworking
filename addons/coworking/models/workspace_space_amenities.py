from odoo import models, fields

class WorkspaceSpaceAmenity(models.Model):
    _name = 'workspace.space.amenity'
    _description = 'Workspace Space Amenities'
    _rec_name = 'space_id'

    space_id = fields.Many2one('workspace.space', string='Space', required=True)
    amenity_id = fields.Many2one('workspace.amenity', string='Amenity', required=True)
    quantity = fields.Integer(string='Quantity', default=1)