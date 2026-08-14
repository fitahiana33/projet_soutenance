import logging
import time
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class DolibarrClient:

    def __init__(self):
        self.base_url = settings.DOLIBARR_BASE_URL.rstrip("/")
        self.api_key = settings.DOLIBARR_API_KEY

    def _headers(self) -> Dict[str, str]:
        return {
            "DOLAPIKEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Teste la connexion avec l'API Dolibarr et retourne le statut et temps de réponse."""
        url = f"{self.base_url}/api/index.php/status"
        start_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    timeout=5.0
                )
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                if response.status_code == 200:
                    data = response.json()
                    version = data.get("dolibarr", {}).get("version", "Inconnue") if isinstance(data, dict) else "23.0.3"
                    return {
                        "connected": True,
                        "base_url": self.base_url,
                        "message": "Connexion à l'API Dolibarr établie avec succès.",
                        "version": version,
                        "response_time_ms": elapsed_ms
                    }
                else:
                    return {
                        "connected": False,
                        "base_url": self.base_url,
                        "message": f"Erreur HTTP Dolibarr {response.status_code}: {response.text[:100]}",
                        "response_time_ms": elapsed_ms
                    }
        except httpx.RequestError as exc:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Dolibarr connection test failed: {exc}")
            return {
                "connected": False,
                "base_url": self.base_url,
                "message": f"Impossible de contacter l'API Dolibarr ({self.base_url}): {str(exc)}",
                "response_time_ms": elapsed_ms
            }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Effectue une requête GET générique vers l'API Dolibarr."""
        url = f"{self.base_url}/api/index.php/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    params=params,
                    timeout=15.0
                )

            if response.status_code == 404:
                return []

            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else [data] if data else []
        except Exception as e:
            logger.error(f"Error fetching from Dolibarr endpoint {endpoint}: {e}")
            raise

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Création directe dans Dolibarr via l'API REST."""
        url = f"{self.base_url}/api/index.php/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._headers(),
                    json=json_data,
                    timeout=15.0
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error POSTing to Dolibarr endpoint {endpoint}: {e}")
            raise

    async def put(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mise à jour directe dans Dolibarr via l'API REST."""
        url = f"{self.base_url}/api/index.php/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers=self._headers(),
                    json=json_data,
                    timeout=15.0
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error PUTting to Dolibarr endpoint {endpoint}: {e}")
            raise

    async def delete(self, endpoint: str) -> bool:
        """Suppression directe dans Dolibarr via l'API REST."""
        url = f"{self.base_url}/api/index.php/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=self._headers(),
                    timeout=15.0
                )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error DELETEing Dolibarr endpoint {endpoint}: {e}")
            raise

    # --- ENTITY FETCHING METHODS ---

    async def get_products(self, min_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère la liste des Produits et Stocks depuis Dolibarr."""
        params = {"sortfield": "t.rowid", "sortorder": "DESC", "limit": 100}
        if min_date:
            params["sqlfilters"] = f"(tms:>='{min_date}')"
        return await self.get("products", params=params)

    async def get_thirdparties(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère les Tierces Parties (Clients & Fournisseurs) depuis Dolibarr."""
        params = {"sortfield": "t.rowid", "sortorder": "DESC", "limit": 100}
        if category == "supplier":
            params["sqlfilters"] = "(fournisseur:=1)"
        elif category == "customer":
            params["sqlfilters"] = "(client:=1)"
        return await self.get("thirdparties", params=params)

    async def get_orders(self) -> List[Dict[str, Any]]:
        """Récupère les Commandes de Ventes & Achats depuis Dolibarr."""
        return await self.get("orders", params={"limit": 100})

    async def get_invoices(self) -> List[Dict[str, Any]]:
        """Récupère les Factures depuis Dolibarr."""
        return await self.get("invoices", params={"limit": 100})

    async def get_users(self) -> List[Dict[str, Any]]:
        """Récupère les Utilisateurs / Employés depuis Dolibarr."""
        return await self.get("users", params={"limit": 100})


dolibarr_client = DolibarrClient()