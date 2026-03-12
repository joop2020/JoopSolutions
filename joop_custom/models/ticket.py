from odoo import api, fields, models, tools, _


class Ticket(models.Model):
    _name = 'ticket.type'
    _description = 'Ticket type'


    name = fields.Char(string='Tipo de ticket')