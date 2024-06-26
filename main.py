import logging
import sys

from db.create_db import create_db, create_db_connection
from providers.fipe.api import FipeApi, FipeApiRequestException

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
)

fipe_api = FipeApi()


def populate_tabela_referencia(conn):
    tabelas_referencia = fipe_api.get_tabelas_de_referencia()
    fipe_api.insert_tabelas_de_referencia(conn, tabelas_referencia)


def populate_marcas(conn, codigo_tabela_referencia):
    marcas = fipe_api.get_marcas(codigo_tabela_referencia)
    fipe_api.insert_marcas(conn, marcas)


def populate_modelos(conn, codigo_tabela_referencia, codigo_marca):
    modelos = fipe_api.get_modelos(codigo_tabela_referencia, codigo_marca)
    fipe_api.insert_modelos(conn, codigo_marca, modelos)


def populate_anos_modelo(conn, codigo_tabela_referencia, codigo_marca, codigo_modelo):
    anos_modelo = fipe_api.get_anos_modelo(
        codigo_tabela_referencia, codigo_marca, codigo_modelo
    )
    fipe_api.insert_ano_modelo(conn, codigo_modelo, anos_modelo)


def get_price(
    conn, codigo_tabela_referencia, codigo_marca, codigo_modelo, codigo_ano_modelo
):
    car_price = fipe_api.get_price(
        codigo_tabela_referencia, codigo_marca, codigo_modelo, codigo_ano_modelo
    )
    fipe_api.insert_price(conn, car_price)


def populate_all_prices_for_modelo(conn, codigo_marca, codigo_modelo):
    ref_tables = fipe_api.get_tabelas_de_referencia()
    stop_iter = False
    for year in range(2010, 2025):
        if stop_iter:
            break

        for ref_table_code, ref_table_name in ref_tables[year]:
            logging.info("Populating prices for %s - %s", year, ref_table_name)

            try:
                anos_modelo = fipe_api.get_anos_modelo(
                    ref_table_code, codigo_marca, codigo_modelo
                )
            except FipeApiRequestException:
                continue

            fipe_api.insert_ano_modelo(conn, codigo_modelo, anos_modelo)

            for _, ano_modelo_code in anos_modelo.items():
                ano = int(ano_modelo_code.split("-")[0])
                try:
                    price = fipe_api.get_price(
                        ref_table_code, codigo_marca, codigo_modelo, ano
                    )
                except FipeApiRequestException:
                    stop_iter = True
                    continue

                fipe_api.insert_price(conn, price)


def populate_all_prices_for_marca(conn, codigo_marca):
    ref_tables = fipe_api.get_tabelas_de_referencia()
    stop_iter = False
    for year in range(2020, 2025):
        if stop_iter:
            break

        for ref_table_code, ref_table_name in ref_tables[year]:
            logging.info("Populating prices for %s - %s", year, ref_table_name)

            try:
                modelos = fipe_api.get_modelos(ref_table_code, codigo_marca)
            except FipeApiRequestException:
                continue

            fipe_api.insert_modelos(conn, codigo_marca, modelos)

            for _, modelo_code in modelos.items():
                try:
                    anos_modelo = fipe_api.get_anos_modelo(
                        ref_table_code, codigo_marca, modelo_code
                    )
                except FipeApiRequestException:
                    continue

                fipe_api.insert_ano_modelo(conn, modelo_code, anos_modelo)

                for _, ano_modelo_code in anos_modelo.items():
                    ano = int(ano_modelo_code.split("-")[0])
                    try:
                        price = fipe_api.get_price(
                            ref_table_code, codigo_marca, modelo_code, ano
                        )
                    except FipeApiRequestException:
                        stop_iter = True
                        continue

                    fipe_api.insert_price(conn, price)


def main():
    conn = create_db_connection()

    create_db(conn)

    args = sys.argv[1:]

    if len(args) == 1:
        populate_all_prices_for_marca(conn, args[0])

    elif len(args) == 2:
        populate_all_prices_for_modelo(conn, args[0], args[1])

    else:
        logging.error("Invalid number of arguments")
        logging.error("Usage: python main.py <codigo_marca> <codigo_modelo>")
        sys.exit(1)

    conn.close()


if __name__ == "__main__":
    main()
