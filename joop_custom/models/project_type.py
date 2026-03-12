from odoo import fields, models


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Tipo de Proyecto'
    _order = 'sequence, name'

    name = fields.Char(string='Nombre', required=True, translate=True)
    description = fields.Text(string='Descripción')
    project_template_id = fields.Many2one(
        'project.project',
        string='Plantilla de Proyecto',
        domain="[('is_template', '=', True)]",
        help='Plantilla que se usará al crear proyectos de este tipo'
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color')