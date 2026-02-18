from odoo import models, fields

class WorkspaceAmenity(models.Model):
    _name = 'workspace.amenity'
    _description = 'Workspace Amenity'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    icon = fields.Char(string='Icon', help='Font Awesome icon class')