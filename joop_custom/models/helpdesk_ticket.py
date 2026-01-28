from odoo import api, fields, models, tools, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_type_id = fields.Many2one(
        comodel_name='ticket.type',
        string='Tipo de ticket'
    )