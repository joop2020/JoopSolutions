from odoo import fields, models


class JoopEquipmentType(models.Model):
    _name = 'joop.equipment.type'
    _description = 'Tipo de equipo para revisión de actualización (FSM Joop)'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)