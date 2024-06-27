from tqdm import tqdm
import logging

from .api import FipeApi, FipeApiRequestException
from db.create_db import create_db_connection

logger = logging.getLogger(__name__)


class FipeCrawler:
    def __init__(self, db_conn=None) -> None:
        self.fipe_api = FipeApi()
        self.conn = db_conn or create_db_connection()

    def populate_prices_for_year(self, year):
        tabelas_referencia = self.fipe_api.get_tabelas_de_referencia()

        _iterable = tqdm(tabelas_referencia[year], desc="Tabela Referência")
        for ref_table_code, ref_table_name in _iterable:
            logger.info("Buscando preços para a tabela referência: %s", ref_table_name)

            self.populate_prices_for_tabela_referencia(ref_table_code)

    def populate_prices_for_tabela_referencia(self, codigo_tabela_referencia):
        marcas = self.fipe_api.get_marcas(codigo_tabela_referencia)
        for marca_name, marca_code in tqdm(marcas.items(), desc="Marcas"):
            logger.info("Buscando preços para a marca: %s", marca_name)

            self.populate_prices_for_marca(codigo_tabela_referencia, marca_code)

    def populate_prices_for_marca(self, codigo_tabela_referencia, codigo_marca):
        try:
            modelos = self.fipe_api.get_modelos(codigo_tabela_referencia, codigo_marca)
        except FipeApiRequestException:
            logger.error("Failed to get modelos for %s", codigo_tabela_referencia)
            return

        logger.info("%s modelos encontrados", len(modelos))

        self.fipe_api.insert_modelos(self.conn, codigo_marca, modelos)

        _iterable = tqdm(modelos.items(), leave=False, desc="Modelos")
        for modelo_name, modelo_code in _iterable:
            logger.debug("Buscando preços para o modelo %s", modelo_name)

            self.populate_prices_for_modelo(
                codigo_tabela_referencia, codigo_marca, modelo_code
            )

    def populate_prices_for_modelo(
        self, codigo_tabela_referencia, codigo_marca, modelo_code
    ):
        try:
            anos_modelo = self.fipe_api.get_anos_modelo(
                codigo_tabela_referencia, codigo_marca, modelo_code
            )
        except FipeApiRequestException:
            logger.error(
                "Failed to get anos_modelo for %s on %s",
                modelo_code,
                codigo_tabela_referencia,
            )
            return

        logger.debug("%s ano-modelos encontrados", len(anos_modelo))

        self.fipe_api.insert_ano_modelo(self.conn, modelo_code, anos_modelo)

        _iterable = tqdm(anos_modelo.items(), leave=False, desc="AnosModelo")
        for _, ano_modelo_code in _iterable:
            logger.debug("Buscando preços para o ano modelo: %s", ano_modelo_code)

            self.populate_prices_for_ano_modelo(
                codigo_tabela_referencia, codigo_marca, modelo_code, ano_modelo_code
            )

    def populate_prices_for_ano_modelo(
        self, codigo_tabela_referencia, codigo_marca, codigo_modelo, ano_modelo_code
    ):
        ano, tipo_combustivel = ano_modelo_code.split("-")
        try:
            price = self.fipe_api.get_price(
                codigo_tabela_referencia,
                codigo_marca,
                codigo_modelo,
                ano,
                codigo_tipo_combustivel=tipo_combustivel,
            )
        except FipeApiRequestException as exc:
            logger.error(
                "Failed to get price for %s - %s - %s - %s",
                codigo_tabela_referencia,
                codigo_marca,
                codigo_modelo,
                ano,
            )
            logger.error(exc)
            raise exc

        self.fipe_api.insert_price(self.conn, price)
