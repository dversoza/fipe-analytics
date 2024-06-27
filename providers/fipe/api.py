import json
import locale
import logging
import os
import time
from datetime import datetime
from hashlib import sha256

import requests

from providers.fipe.exceptions import FipeApiRequestException

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

    def _hash_request(self, endpoint, params):
        return sha256(f"{endpoint}{params}".encode()).hexdigest()

    def _cache_request(self, endpoint, params, response):
        _hash = self._hash_request(endpoint, params)
        with open(f"{self.REQUEST_CACHE_DIR}/{_hash}.json", "w", encoding="utf-8") as f:
            f.write(response)

    def _get_cached_response(self, endpoint, params, cache_expire=None):
        _hash = self._hash_request(endpoint, params)
        _cached_file_path = f"{self.REQUEST_CACHE_DIR}/{_hash}.json"

        _cached_file_last_modified = os.path.getmtime(_cached_file_path)
        if cache_expire and time.time() - _cached_file_last_modified > cache_expire:
            os.remove(_cached_file_path)
            raise FileNotFoundError

        with open(_cached_file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _delete_cached_response(self, endpoint, params):
        _hash = self._hash_request(endpoint, params)
        _cached_file_path = f"{self.REQUEST_CACHE_DIR}/{_hash}.json"

        if os.path.exists(_cached_file_path):
            os.remove(_cached_file_path)

    def _make_request_raw(self, url, params, retry_count=0):
        response = requests.post(url, params=params, timeout=10)

        if response.status_code == 200:
            time.sleep(0.5)

            return response.text

        logger.error("Request to failed with status code %s", response.status_code)
        logger.debug("URL: %s", url)
        logger.debug("Params: %s", params)
        logger.debug("Response: %s", response.text)

        if response.status_code == 429:
            logger.error("Cloudflare protection triggered. Waiting 10 seconds.")
            time.sleep(10)

        if response.status_code == 520:
            logger.error("Cloudflare error. Waiting 5 seconds.")
            time.sleep(5)

        if retry_count < 3:
            logger.error("Retrying request...")
            return self._make_request_raw(url, params, retry_count + 1)

    def _make_request(self, endpoint, params=None, cache_expire=None):
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
            raise FipeApiRequestException(response_json.get("erro"))

        return response_json

    def get_tabelas_de_referencia(self):
        raw_tabelas_de_referencia = self._make_request(
            "/ConsultarTabelaDeReferencia", cache_expire=ONE_MONTH
        )

        return self.process_tabelas_de_referencia(raw_tabelas_de_referencia)

    def process_tabelas_de_referencia(
        self, raw_tabelas_de_referencia: list[dict[str, str]]
    ) -> dict[str, list[tuple[str, str]]]:
        """Process raw tabelas de referencia into a more usable format.

        Raw example:
        [
            {
                "Codigo": "001",
                "Mes": "janeiro/2018"
            },
            {
                "Codigo": "002",
                "Mes": "fevereiro/2018"
            }
        ]

        Processed example:
        {
            "2018": [
                ("001", "janeiro/2018"),
                ("002", "fevereiro/2018")
            ]
        }
        """
        result = {}

        for entry in raw_tabelas_de_referencia:
            _year = int(entry["Mes"].split("/")[1].strip())
            if _year not in result:
                result[_year] = [(entry["Codigo"], entry["Mes"])]
            else:
                result[_year].append((entry["Codigo"], entry["Mes"]))

        return result

    def insert_tabelas_de_referencia(self, conn, tabelas_de_referencia):
        cur = conn.cursor()

        for year, tables in tabelas_de_referencia.items():
            for codigo, mes_nome in tables:
                mes_int = _mes_str_to_int(mes_nome.split("/")[0])

                cur.execute(
                    """
                    INSERT INTO tabela_referencia (
                        fipe_id,
                        display_name,
                        mes,
                        ano
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    ) ON CONFLICT (fipe_id) DO NOTHING
                    """,
                    (codigo, mes_nome, mes_int, int(year)),
                )

            conn.commit()

        cur.close()

        return conn

    def get_marcas(self, codigo_tabela_referencia, codigo_tipo_veiculo=1):
        """
        Tipos de Veículo:
        1 - Carros
        2 - Motos
        3 - Caminhões e Micro-Ônibus
        """
        _params = {
            "codigoTabelaReferencia": str(codigo_tabela_referencia),
            "codigoTipoVeiculo": str(codigo_tipo_veiculo),
        }

        raw_marcas = self._make_request("/ConsultarMarcas", _params)

        return self.process_marcas(raw_marcas)

    def process_marcas(self, raw_marcas: list[dict[str, str]]) -> dict[str, str]:
        """Process raw marcas into a more usable format.

        Raw example:
        [
            {
                "Label": "Acura",
                "Value": "1"
            },
            {
                "Label": "Agrale",
                "Value": "2"
            }
        ]

        Processed example:
        {
            "acura": "1",
            "agrale": "2"
        }
        """
        return {brand["Label"]: brand["Value"] for brand in raw_marcas}

    def insert_marcas(self, conn, marcas):
        cur = conn.cursor()

        for brand, fipe_id in marcas.items():
            cur.execute(
                """
                INSERT INTO marca (
                    fipe_id,
                    display_name
                ) VALUES (
                    %s,
                    %s
                ) ON CONFLICT (fipe_id) DO NOTHING
                """,
                (fipe_id, brand),
            )

            conn.commit()

        cur.close()

        return conn

    def get_modelos(
        self, codigo_tabela_referencia, codigo_marca, codigo_tipo_veiculo=1
    ):
        _params = {
            "codigoTabelaReferencia": str(codigo_tabela_referencia),
            "codigoTipoVeiculo": str(codigo_tipo_veiculo),
            "codigoMarca": str(codigo_marca),
        }

        raw_modelos = self._make_request("/ConsultarModelos", _params)

        return self.process_modelos(raw_modelos["Modelos"])

    def process_modelos(self, raw_modelos: list[dict[str, str]]) -> dict[str, str]:
        """Process raw modelos into a more usable format.

        Raw example:
        [
            {
                "Label": "A1",
                "Value": "1"
            },
            {
                "Label": "A3",
                "Value": "2"
            }
        ]

        Processed example:
        {
            "A1": "1",
            "A3": "2"
        }
        """
        return {model["Label"]: model["Value"] for model in raw_modelos}

    def insert_modelos(self, conn, marca_id, modelos):
        cur = conn.cursor()

        for model, fipe_id in modelos.items():
            cur.execute(
                """
                INSERT INTO modelo (
                    fipe_id,
                    marca_id,
                    display_name,
                    tipo_veiculo
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                ) ON CONFLICT (fipe_id) DO NOTHING
                """,
                (fipe_id, marca_id, model, 1),
            )

            conn.commit()

        cur.close()

        return conn

    def get_anos_modelo(
        self,
        codigo_tabela_referencia,
        codigo_marca,
        codigo_modelo,
        codigo_tipo_veiculo=1,
    ):
        _params = {
            "codigoTabelaReferencia": str(codigo_tabela_referencia),
            "codigoMarca": str(codigo_marca),
            "codigoModelo": str(codigo_modelo),
            "codigoTipoVeiculo": str(codigo_tipo_veiculo),
        }

        raw_ano_modelo = self._make_request("/ConsultarAnoModelo", _params)

        return self.process_anos_modelo(raw_ano_modelo)

    def process_anos_modelo(
        self, raw_ano_modelo: list[dict[str, str]]
    ) -> dict[str, str]:
        """Process raw ano modelo into a more usable format.

        Raw example:
        [
            {
                "Label": "2020 Gasolina",
                "Value": "2020-1"
            },
            {
                "Label": "2020 Álcool",
                "Value": "2020-3"
            }
        ]

        Processed example:
        {
            "2020 Gasolina": "2020-1",
            "2020 Álcool": "2020-3"
        }
        """
        return {ano["Label"]: ano["Value"] for ano in raw_ano_modelo}

    def insert_ano_modelo(self, conn, modelo_id, anos_modelo):
        cur = conn.cursor()

        for display_name, fipe_id in anos_modelo.items():
            year, fuel_type = fipe_id.split("-")
            cur.execute(
                """
                INSERT INTO ano_modelo (
                    fipe_id,
                    modelo_id,
                    display_name,
                    ano,
                    tipo_combustivel
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                ) ON CONFLICT (fipe_id, modelo_id) DO NOTHING
                """,
                (fipe_id, modelo_id, display_name, year, fuel_type),
            )

            conn.commit()

        cur.close()

        return conn

    def get_price(
        self,
        codigo_tabela_referencia,
        codigo_marca,
        codigo_modelo,
        ano_modelo,
        codigo_tipo_veiculo=1,
        codigo_tipo_combustivel=1,
    ) -> tuple[dict[str, str], dict[str, str]]:
        _params = {
            "codigoTabelaReferencia": str(codigo_tabela_referencia),
            "codigoMarca": str(codigo_marca),
            "codigoModelo": str(codigo_modelo),
            "codigoTipoVeiculo": str(codigo_tipo_veiculo),
            "anoModelo": str(ano_modelo),
            "codigoTipoCombustivel": str(codigo_tipo_combustivel),
            "tipoVeiculo": "carro",
            "tipoConsulta": "tradicional",
        }

        response_json = self._make_request("/ConsultarValorComTodosParametros", _params)

        return self.process_price(response_json, _params)

    def process_price(
        self, raw_price: dict[str, str], request_params: dict[str, str]
    ) -> dict[str, str]:
        """Process raw price into a more usable format."""
        return {
            "codigo_tabela_referencia": request_params["codigoTabelaReferencia"],
            "marca_id": request_params["codigoMarca"],
            "modelo_id": request_params["codigoModelo"],
            "ano_modelo_id": f'{request_params["anoModelo"]}-{request_params["codigoTipoCombustivel"]}',
            "codigo_tipo_veiculo": request_params["codigoTipoVeiculo"],
            "autenticacao": raw_price["Autenticacao"],
            "data": raw_price["DataConsulta"],
            "mesReferencia": raw_price["MesReferencia"].strip(),
            "codigo_fipe_veiculo": raw_price["CodigoFipe"],
            "valor": _price_str_to_float(raw_price["Valor"]),
            "raw_data": json.dumps(raw_price),
        }

    def insert_price(self, conn, price):
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO preco (
                marca_id,
                modelo_id,
                ano_modelo_id,
                codigo_tipo_veiculo,
                codigo_tabela_referencia,
                autenticacao,
                data_consulta,
                mes_referencia,
                valor,
                codigo_fipe_veiculo,
                raw_data
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (autenticacao) DO UPDATE SET
                valor = EXCLUDED.valor,
                data_consulta = EXCLUDED.data_consulta,
                raw_data = EXCLUDED.raw_data
            """,
            (
                price["marca_id"],
                price["modelo_id"],
                price["ano_modelo_id"],
                price["codigo_tipo_veiculo"],
                price["codigo_tabela_referencia"],
                price["autenticacao"],
                price["data"],
                price["mesReferencia"],
                price["valor"],
                price["codigo_fipe_veiculo"],
                price["raw_data"],
            ),
        )

        cur.close()

        return conn
