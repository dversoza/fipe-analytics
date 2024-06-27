import logging

from sqlalchemy.orm import Session
from tqdm import tqdm

from db import services as db_services
from db.engine import create_db_engine
from providers.fipe.api import FipeApi
from providers.fipe.services import FipeDatabaseRepository

logger = logging.getLogger(__name__)


class FipeCrawler:
    def __init__(self, checkpoint: dict | None = None) -> None:
        self.fipe_api = FipeApi()
        self.fipe_db_repo = FipeDatabaseRepository()
        self.db_session = Session(bind=create_db_engine())

        self._checkpoint = checkpoint or {}

    def populate_reference_tables_in_ascending_order(
        self, year_lte: int = 2002, vehicle_type_id: int = 1
    ):
        _reference_tables = db_services.list_reference_tables(
            self.db_session, year_lte=year_lte
        )
        _checkpoint_year = self._checkpoint.get("year", 0)
        _checkpoint_month = self._checkpoint.get("month", 0)
        for reference_table in _reference_tables:
            if reference_table.year < _checkpoint_year:
                continue

            if reference_table.month < _checkpoint_month:
                continue

            self._checkpoint["year"] = reference_table.year
            self._checkpoint["month"] = reference_table.month

            self.populate_prices_for_reference_table(
                reference_table_id=reference_table.fipe_id,
                vehicle_type_id=vehicle_type_id,
            )

            self._checkpoint["manufacturer"] = 0
            self._checkpoint["model"] = 0
            self._checkpoint["year_model"] = 0

    def populate_prices_for_reference_table(
        self, reference_table_id: str, vehicle_type_id: int = 1
    ):
        manufacturers_response = self.fipe_api.get_manufacturers(
            reference_table_id, vehicle_type_id
        )
        self.fipe_db_repo.persist_manufacturers(manufacturers_response, vehicle_type_id)
        manufacturers = sorted(
            manufacturers_response.manufacturers, key=lambda x: int(x.code)
        )
        _checkpoint_manufacturer = self._checkpoint.get("manufacturer", 0)
        for manufacturer in tqdm(manufacturers, desc="Marcas"):
            if int(manufacturer.code) < _checkpoint_manufacturer:
                continue

            logger.info("Processando Marca: %s", manufacturer.display_name)

            self._checkpoint["manufacturer"] = int(manufacturer.code)

            self.populate_prices_for_manufacturer(
                reference_table_id, manufacturer.code, vehicle_type_id
            )

            self._checkpoint["model"] = 0
            self._checkpoint["year_model"] = 0

    def populate_prices_for_manufacturer(
        self, reference_table_id: str, manufacturer_id: str, vehicle_type_id: int = 1
    ):
        car_models_response = self.fipe_api.get_car_models(
            reference_table_id=reference_table_id,
            manufacturer_id=manufacturer_id,
            vehicle_type_id=vehicle_type_id,
        )
        self.fipe_db_repo.persist_car_models(car_models_response, manufacturer_id)

        car_models = sorted(car_models_response.car_models, key=lambda x: int(x.code))
        _checkpoint_model = self._checkpoint.get("model", 0)
        for car_model in tqdm(car_models, desc="Modelos", leave=False):
            if int(car_model.code) < _checkpoint_model:
                continue

            logger.info("\tModelo: %s", car_model.display_name)

            self._checkpoint["model"] = int(car_model.code)

            self.populate_prices_for_car_model(
                reference_table_id, manufacturer_id, car_model.code, vehicle_type_id
            )

            self._checkpoint["year_model"] = 0

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

        car_model_years = sorted(
            car_model_years_response.car_model_years,
            key=lambda x: int(x.code.split("-")[0]),
        )
        for car_model_year in tqdm(car_model_years, desc="AnoModelo", leave=False):
            year_str, fuel_type_str = car_model_year.code.split("-")

            logger.debug("\t\tAno-modelo: %s", car_model_year.display_name)

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

    def get_checkpoint(self):
        return self._checkpoint
