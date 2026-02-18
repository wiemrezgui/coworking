from odoo import models, fields

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