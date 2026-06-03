import json

from odoo import fields, models
from odoo.exceptions import UserError


class SyscomTestWizard(models.TransientModel):
    """Asistente para probar la conexión y explorar la información que
    devuelve el API de SYSCOM.
    """

    _name = "joop.syscom.test.wizard"
    _description = "Consulta al API de SYSCOM"

    operation = fields.Selection(
        selection=[
            ("categorias", "Categorías"),
            ("marcas", "Marcas"),
            ("tipocambio", "Tipo de cambio"),
            ("buscar", "Buscar productos"),
            ("producto", "Detalle de producto"),
        ],
        string="Operación",
        default="buscar",
        required=True,
    )

    # Parámetros de búsqueda
    busqueda = fields.Char(string="Búsqueda (palabras clave)")
    categoria = fields.Char(string="ID Categoría")
    marca = fields.Char(string="ID/Nombre Marca")
    orden = fields.Selection(
        selection=[
            ("relevancia", "Relevancia"),
            ("topseller", "Más vendidos"),
            ("precio:asc", "Precio ascendente"),
            ("precio:desc", "Precio descendente"),
            ("modelo:asc", "Modelo A-Z"),
            ("modelo:desc", "Modelo Z-A"),
        ],
        string="Orden",
        default="relevancia",
    )
    pagina = fields.Integer(string="Página", default=1)
    solo_stock = fields.Boolean(string="Sólo con existencia")

    # Parámetro de detalle
    producto_id = fields.Char(string="ID de producto")

    # Resultado
    result_json = fields.Text(string="Respuesta (JSON)", readonly=True)
    result_summary = fields.Text(string="Resumen", readonly=True)

    def action_run(self):
        self.ensure_one()
        api = self.env["joop.syscom.api"]

        if self.operation == "categorias":
            data = api.get_categorias()
        elif self.operation == "marcas":
            data = api.get_marcas()
        elif self.operation == "tipocambio":
            data = api.get_tipo_cambio()
        elif self.operation == "producto":
            if not self.producto_id:
                raise UserError("Indique el ID de producto.")
            data = api.get_producto(self.producto_id.strip())
        else:  # buscar
            data = api.search_productos(
                busqueda=self.busqueda,
                categoria=self.categoria,
                marca=self.marca,
                orden=self.orden,
                pagina=self.pagina or 1,
                stock=self.solo_stock,
            )

        self.result_json = json.dumps(data, indent=2, ensure_ascii=False)
        self.result_summary = self._summarize(data)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _summarize(self, data):
        """Genera un resumen legible según el tipo de respuesta."""
        if isinstance(data, dict) and "productos" in data:
            lines = [
                "Encontrados: %s | Página %s de %s" % (
                    data.get("cantidad"), data.get("pagina"), data.get("paginas"),
                ),
                "",
            ]
            for p in data.get("productos", []):
                precios = p.get("precios") or {}
                lines.append(
                    "[%s] %s — %s | existencia: %s | lista: %s / desc: %s" % (
                        p.get("producto_id"),
                        p.get("modelo"),
                        p.get("titulo"),
                        p.get("total_existencia"),
                        precios.get("precio_lista"),
                        precios.get("precio_descuentos"),
                    )
                )
            return "\n".join(lines)

        if isinstance(data, dict) and "producto_id" in data:
            precios = data.get("precios") or {}
            return "\n".join([
                "ID: %s" % data.get("producto_id"),
                "Modelo: %s" % data.get("modelo"),
                "Título: %s" % data.get("titulo"),
                "Marca: %s" % data.get("marca"),
                "SAT: %s" % data.get("sat_key"),
                "Existencia total: %s" % data.get("total_existencia"),
                "Precio lista: %s" % precios.get("precio_lista"),
                "Precio especial: %s" % precios.get("precio_especial"),
                "Precio descuentos: %s" % precios.get("precio_descuentos"),
            ])

        if isinstance(data, list):
            return "Elementos devueltos: %s" % len(data)
        return ""