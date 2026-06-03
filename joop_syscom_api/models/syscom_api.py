import logging
from datetime import datetime, timedelta

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Endpoints SYSCOM
TOKEN_URL = "https://developers.syscom.mx/oauth/token"
API_BASE = "https://developers.syscom.mx/api/v1"

# Claves usadas en ir.config_parameter
PARAM_CLIENT_ID = "joop_syscom_api.client_id"
PARAM_CLIENT_SECRET = "joop_syscom_api.client_secret"
PARAM_TOKEN = "joop_syscom_api.access_token"
PARAM_TOKEN_EXPIRY = "joop_syscom_api.token_expiry"

# Margen de seguridad para refrescar el token antes de que expire (segundos)
TOKEN_REFRESH_MARGIN = 3600
DEFAULT_TIMEOUT = 30


class SyscomApi(models.AbstractModel):
    """Servicio de conexión con el API de SYSCOM.

    Modelo abstracto (sin tabla): centraliza la autenticación OAuth2 y el
    acceso a los recursos del API. Otros modelos lo usan vía
    ``self.env['joop.syscom.api'].<metodo>()``.
    """

    _name = "joop.syscom.api"
    _description = "Syscom API Connector"

    # ------------------------------------------------------------------
    # Credenciales / Token
    # ------------------------------------------------------------------
    def _get_credentials(self):
        ICP = self.env["ir.config_parameter"].sudo()
        client_id = ICP.get_param(PARAM_CLIENT_ID)
        client_secret = ICP.get_param(PARAM_CLIENT_SECRET)
        if not client_id or not client_secret:
            raise UserError(_(
                "Faltan las credenciales de SYSCOM. Configúrelas en "
                "Ajustes > Ajustes generales > Syscom API."
            ))
        return client_id, client_secret

    def _fetch_token(self):
        """Solicita un nuevo access_token a SYSCOM y lo cachea."""
        client_id, client_secret = self._get_credentials()
        try:
            response = requests.post(
                TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            _logger.exception("Error solicitando token a SYSCOM")
            raise UserError(_("No se pudo conectar con SYSCOM: %s") % exc)

        if response.status_code != 200:
            raise UserError(_(
                "SYSCOM rechazó las credenciales (HTTP %(code)s): %(body)s",
                code=response.status_code,
                body=response.text[:500],
            ))

        data = response.json()
        token = data.get("access_token")
        expires_in = int(data.get("expires_in") or 0)
        if not token:
            raise UserError(_("SYSCOM no devolvió un access_token. Respuesta: %s")
                            % response.text[:500])

        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param(PARAM_TOKEN, token)
        ICP.set_param(PARAM_TOKEN_EXPIRY, expiry.isoformat())
        # _logger.info("Token SYSCOM renovado, expira %s", expiry.isoformat())
        return token

    def _get_token(self, force_refresh=False):
        """Devuelve un token válido, renovándolo si es necesario."""
        ICP = self.env["ir.config_parameter"].sudo()
        token = ICP.get_param(PARAM_TOKEN)
        expiry_raw = ICP.get_param(PARAM_TOKEN_EXPIRY)

        if force_refresh or not token or not expiry_raw:
            return self._fetch_token()

        try:
            expiry = datetime.fromisoformat(expiry_raw)
        except ValueError:
            return self._fetch_token()

        if datetime.utcnow() >= (expiry - timedelta(seconds=TOKEN_REFRESH_MARGIN)):
            return self._fetch_token()
        return token

    # ------------------------------------------------------------------
    # Petición genérica
    # ------------------------------------------------------------------
    def _request(self, endpoint, params=None, method="GET", _retry=True):
        """Hace una petición autenticada al API y devuelve el JSON.

        :param endpoint: ruta relativa al API, p.ej. ``"categorias"`` o
            ``"productos/12345"``.
        :param params: dict de parámetros de query string.
        """
        token = self._get_token()
        url = "%s/%s" % (API_BASE, endpoint.lstrip("/"))
        try:
            response = requests.request(
                method,
                url,
                headers={"Authorization": "Bearer %s" % token},
                params=params or {},
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            _logger.exception("Error en petición a SYSCOM %s", url)
            raise UserError(_("Error de conexión con SYSCOM: %s") % exc)

        # Token expirado/invalidado: reintentar una vez con token nuevo.
        if response.status_code == 401 and _retry:
            self._get_token(force_refresh=True)
            return self._request(endpoint, params=params, method=method, _retry=False)

        if response.status_code != 200:
            raise UserError(_(
                "SYSCOM respondió HTTP %(code)s en %(endpoint)s: %(body)s",
                code=response.status_code,
                endpoint=endpoint,
                body=response.text[:500],
            ))

        try:
            return response.json()
        except ValueError:
            raise UserError(_("SYSCOM devolvió una respuesta no-JSON: %s")
                            % response.text[:500])

    # ------------------------------------------------------------------
    # Helpers de alto nivel (recursos)
    # ------------------------------------------------------------------
    @api.model
    def test_connection(self):
        """Verifica credenciales pidiendo un token y un recurso simple."""
        self._get_token(force_refresh=True)
        self._request("categorias")
        return True

    @api.model
    def get_categorias(self):
        return self._request("categorias")

    @api.model
    def get_marcas(self):
        return self._request("marcas")

    @api.model
    def get_tipo_cambio(self):
        return self._request("tipocambio")

    @api.model
    def search_productos(self, busqueda=None, categoria=None, marca=None,
                         orden=None, pagina=1, stock=None):
        """Búsqueda de productos. Requiere al menos uno de:
        busqueda, categoria o marca.
        """
        params = {"pagina": pagina}
        if busqueda:
            # SYSCOM separa palabras clave con "+"
            params["busqueda"] = busqueda.strip().replace(" ", "+")
        if categoria:
            params["categoria"] = categoria
        if marca:
            params["marca"] = marca
        if orden:
            params["orden"] = orden
        if stock is not None:
            params["stock"] = 1 if stock else 0
        if not (busqueda or categoria or marca):
            raise UserError(_(
                "Debe indicar al menos un criterio: búsqueda, categoría o marca."
            ))
        return self._request("productos", params=params)

    @api.model
    def get_producto(self, producto_id):
        """Información detallada de un producto por su ID/modelo."""
        return self._request("productos/%s" % producto_id)