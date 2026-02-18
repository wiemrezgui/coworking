from odoo import models, fields

class WorkspaceType(models.Model):
    _name = 'workspace.type'
    _description = 'Workspace Type'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')