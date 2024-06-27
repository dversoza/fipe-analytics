import logging

from sqlalchemy.orm import Session
from tqdm import tqdm

from db import services as db_services
from db.engine import create_db_engine
from providers.fipe.api import FipeApi
from providers.fipe.services import FipeDatabaseRepository

logger = logging.getLogger(__name__)


class FipeCrawler:
    def __init__(self) -> None:
        self.fipe_api = FipeApi()
        self.fipe_db_repo = FipeDatabaseRepository()
        self.db_session = Session(bind=create_db_engine())

    def populate_old_reference_tables(
        self, year_lte: int = 2002, vehicle_type_id: int = 1
    ):
        _reference_tables = db_services.list_reference_tables(
            self.db_session, year_lte=year_lte
        )
        for reference_table in _reference_tables:
            self.populate_prices_for_reference_table(
                reference_table.fipe_id, vehicle_type_id
            )

    def populate_prices_for_reference_table(
        self, reference_table_id: str, vehicle_type_id: int = 1
    ):
        manufacturers_response = self.fipe_api.get_manufacturers(
            reference_table_id, vehicle_type_id
        )
        self.fipe_db_repo.persist_manufacturers(manufacturers_response, vehicle_type_id)
        for manufacturer in tqdm(manufacturers_response.manufacturers, desc="Marcas"):
            logger.info("Processando Marca: %s", manufacturer.display_name)

            self.populate_prices_for_manufacturer(
                reference_table_id, manufacturer.code, vehicle_type_id
            )

    def populate_prices_for_manufacturer(
        self, reference_table_id: str, manufacturer_id: str, vehicle_type_id: int = 1
    ):
        car_models_response = self.fipe_api.get_car_models(
            reference_table_id=reference_table_id,
            manufacturer_id=manufacturer_id,
            vehicle_type_id=vehicle_type_id,
        )
        self.fipe_db_repo.persist_car_models(car_models_response, manufacturer_id)
        for car_model in tqdm(
            car_models_response.car_models, desc="Modelos", leave=False
        ):
            logger.info("\tModelo: %s", car_model.display_name)

            self.populate_prices_for_car_model(
                reference_table_id, manufacturer_id, car_model.code, vehicle_type_id
            )

    def populate_prices_for_car_model(
        self,
        reference_table_id: str,
        manufacturer_id: str,
        model_id: str,
        vehicle_type_id: int = 1,
    ):
        car_model_years_response = self.fipe_api.get_car_model_years(
            reference_table_id, manufacturer_id, model_id, vehicle_type_id
        )
        self.fipe_db_repo.persist_car_model_years(car_model_years_response, model_id)
        for car_model_year in tqdm(
            car_model_years_response.car_model_years, desc="AnoModelo", leave=False
        ):
            logger.debug("\t\tAno-modelo: %s", car_model_year.display_name)

            year_str, fuel_type_str = car_model_year.code.split("-")

            car_price = self.fipe_api.get_price(
                reference_table_id,
                manufacturer_id,
                model_id,
                year_str,
                vehicle_type_id,
                fuel_type_str,
            )

            self.fipe_db_repo.persist_car_price(
                car_price,
                manufacturer_id,
                model_id,
                car_model_year.code,
                vehicle_type_id,
                reference_table_id,
            )
