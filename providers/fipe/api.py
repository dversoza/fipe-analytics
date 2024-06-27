import json
import locale
import logging
import os
import time
from datetime import datetime
from hashlib import sha256

import requests

from providers.fipe import exceptions
from providers.fipe import schemas

logger = logging.getLogger(__name__)

ONE_MONTH = 3600 * 24 * 30


def _mes_str_to_int(mes):
    # ex. "junho" -> "06"
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    return datetime.strptime(mes, "%B").strftime("%m")


def _price_str_to_float(price_str):
    formatted_str = price_str.replace("R$", "").replace(".", "").replace(",", ".")
    return float(formatted_str)


class FipeApi:
    BASE_URL = "https://veiculos.fipe.org.br/api/veiculos"
    REQUEST_CACHE_DIR = "cache/fipe_raw_responses"

    def _hash_request(self, endpoint: str, params: dict[str, str]) -> str:
        return sha256(f"{endpoint}{params}".encode()).hexdigest()

    def _cache_request(self, endpoint: str, params: dict[str, str], response: str):
        _hash = self._hash_request(endpoint, params)
        with open(f"{self.REQUEST_CACHE_DIR}/{_hash}.json", "w", encoding="utf-8") as f:
            f.write(response)

    def _get_cached_response(
        self,
        endpoint: str,
        params: dict[str, str],
        cache_expire: int | None = None,
    ) -> str:
        _hash = self._hash_request(endpoint, params)
        _cached_file_path = f"{self.REQUEST_CACHE_DIR}/{_hash}.json"

        _cached_file_last_modified = os.path.getmtime(_cached_file_path)
        if cache_expire and time.time() - _cached_file_last_modified > cache_expire:
            os.remove(_cached_file_path)
            raise FileNotFoundError

        with open(_cached_file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _delete_cached_response(self, endpoint: str, params: dict[str, str]) -> None:
        _hash = self._hash_request(endpoint, params)
        _cached_file_path = f"{self.REQUEST_CACHE_DIR}/{_hash}.json"

        if os.path.exists(_cached_file_path):
            os.remove(_cached_file_path)

    def _make_request_raw(
        self,
        url: str,
        params: dict[str, str],
        retry_count: int = 0,
    ) -> str:
        response = requests.post(url, params=params, timeout=10)

        if response.status_code == 200:
            time.sleep(0.5)

            return response.text

        logger.error("Request to failed with status code %s", response.status_code)
        logger.debug("URL: %s", url)
        logger.debug("Params: %s", params)
        logger.debug("Response: %s", response.text)

        if response.status_code == 429:
            logger.error("Too many requests. Waiting 5 seconds.")
            time.sleep(5)

        if response.status_code == 520:
            logger.error("Server response error. Waiting 5 seconds.")
            time.sleep(5)

        if retry_count < 3:
            logger.error("Retrying request...")
            return self._make_request_raw(url, params, retry_count + 1)

        raise exceptions.FipeApiRequestException("Failed to make request")

    def _make_request(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        cache_expire: int | None = None,
    ) -> dict:
        url = self.BASE_URL + endpoint

        try:
            response = self._get_cached_response(endpoint, params, cache_expire)
        except FileNotFoundError:
            response = self._make_request_raw(url, params)
            self._cache_request(endpoint, params, response)

        try:
            response_json = json.loads(response)
        except json.JSONDecodeError as exc:
            logger.error("Error decoding JSON: %s", response)
            self._delete_cached_response(endpoint, params)
            raise exc

        if "erro" in response_json:
            logger.error("Error: %s", response_json.get("erro"))
            raise exceptions.FipeApiRequestException(response_json.get("erro"))

        return response_json

    def get_reference_tables(self) -> schemas.FipeApiReferenceTablesResponseSchema:
        reference_tables_response = self._make_request(
            "/ConsultarTabelaDeReferencia", cache_expire=ONE_MONTH
        )

        return schemas.FipeApiReferenceTablesResponseSchema(
            reference_tables=reference_tables_response
        )

    def get_manufacturers(
        self,
        reference_table_id: int | str,
        vehicle_type_id: int | str = 1,
    ) -> schemas.FipeApiManufacturersResponseSchema:
        """
        Tipos de Veículo:
        1 - Carros
        2 - Motos
        3 - Caminhões e Micro-Ônibus
        """
        _params = {
            "codigoTabelaReferencia": str(reference_table_id),
            "codigoTipoVeiculo": str(vehicle_type_id),
        }

        manufacturers_response = self._make_request("/ConsultarMarcas", _params)

        return schemas.FipeApiManufacturersResponseSchema(
            manufacturers=manufacturers_response
        )

    def get_car_models(
        self,
        reference_table_id: int | str,
        manufacturer_id: int | str,
        vehicle_type_id: int | str = 1,
    ) -> schemas.FipeApiCarModelsResponseSchema:
        _params = {
            "codigoTabelaReferencia": str(reference_table_id),
            "codigoMarca": str(manufacturer_id),
            "codigoTipoVeiculo": str(vehicle_type_id),
        }

        car_models_response = self._make_request("/ConsultarModelos", _params)

        return schemas.FipeApiCarModelsResponseSchema(
            car_models=car_models_response["Modelos"]
        )

    def get_car_model_years(
        self,
        reference_table_id: int | str,
        manufacturer_id: int | str,
        car_model_id: int | str,
        vehicle_type_id: int | str = 1,
    ) -> schemas.FipeApiCarModelYearsResponseSchema:
        _params = {
            "codigoTabelaReferencia": str(reference_table_id),
            "codigoMarca": str(manufacturer_id),
            "codigoModelo": str(car_model_id),
            "codigoTipoVeiculo": str(vehicle_type_id),
        }

        car_model_years_response = self._make_request("/ConsultarAnoModelo", _params)

        return schemas.FipeApiCarModelYearsResponseSchema(
            car_model_years=car_model_years_response
        )

    def get_price(
        self,
        codigo_tabela_referencia,
        codigo_marca,
        codigo_modelo,
        ano_modelo,
        codigo_tipo_veiculo=1,
        codigo_tipo_combustivel=1,
    ) -> schemas.FipeApiCarPriceResponseSchema:
        _params = {
            "codigoTabelaReferencia": str(codigo_tabela_referencia),
            "codigoMarca": str(codigo_marca),
            "codigoModelo": str(codigo_modelo),
            "codigoTipoVeiculo": str(codigo_tipo_veiculo),
            "anoModelo": str(ano_modelo),
            "codigoTipoCombustivel": str(codigo_tipo_combustivel),
            "tipoConsulta": "tradicional",
        }

        car_price_response = self._make_request(
            "/ConsultarValorComTodosParametros", _params
        )

        return schemas.FipeApiCarPriceResponseSchema(
            raw_data=car_price_response,
            **car_price_response,
        )
