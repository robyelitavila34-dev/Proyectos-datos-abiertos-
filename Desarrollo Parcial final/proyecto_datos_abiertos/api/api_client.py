import os
import requests
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    def __init__(self):
        recurso = os.getenv("API_RESOURCE_ID", "2fsd-7enq")
        self.url = f"https://www.datos.gov.co/resource/{recurso}.json"

    def obtener_registros(self, limite=250):
        parametros = {"$limit": limite}
        respuesta = requests.get(
            self.url,
            params=parametros,
            timeout=20
        )
        respuesta.raise_for_status()
        return respuesta.json()
