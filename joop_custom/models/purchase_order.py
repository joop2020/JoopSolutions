from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    task_id = fields.Many2one(
        'project.task',
        string='Tarea',
        help='Tarea desde la que se creó esta orden de compra'
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.task_id:
                order.task_id.purchase_order_ids = [(4, order.id)]
        return orders

    def write(self, vals):
        old_task_ids = {order.id: order.task_id for order in self}
        result = super().write(vals)
        if 'task_id' in vals:
            for order in self:
                old_task = old_task_ids.get(order.id)
                new_task = order.task_id
                if old_task and old_task != new_task:
                    old_task.purchase_order_ids = [(3, order.id)]
                if new_task and new_task != old_task:
                    new_task.purchase_order_ids = [(4, order.id)]
        return result