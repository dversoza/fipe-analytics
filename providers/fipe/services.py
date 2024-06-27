import json
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from db.engine import create_db_engine
from db.models import all_models as db_models
from providers.fipe import schemas as fipe_schemas
from providers.fipe.utils import convert_month_str_to_int, convert_brl_str_to_float


class FipeDatabaseRepository:
    def __init__(self) -> None:
        self._engine = create_db_engine()
        self._session = Session(bind=self._engine)

    def persist_reference_table(
        self, reference_table: fipe_schemas.FipeApiReferenceTableSchema
    ) -> None:
        month_str, year_str = reference_table.display_name.split("/")

        year = int(year_str.strip())
        month = convert_month_str_to_int(month_str)

        stmt = (
            insert(db_models.ReferenceTable)
            .values(
                fipe_id=reference_table.code,
                display_name=reference_table.display_name,
                month=month,
                year=year,
            )
            .on_conflict_do_nothing(index_elements=["fipe_id"])
        )

        self._session.execute(stmt)
        self._session.commit()

    def persist_reference_tables(
        self, reference_tables: fipe_schemas.FipeApiReferenceTablesResponseSchema
    ) -> None:
        for reference_table in reference_tables.reference_tables:
            self.persist_reference_table(reference_table)

    def persist_manufacturer(
        self,
        manufacturer: fipe_schemas.FipeApiManufacturerSchema,
        vehicle_type_id: int,
    ) -> None:
        stmt = (
            insert(db_models.Manufacturer)
            .values(
                fipe_id=manufacturer.code,
                display_name=manufacturer.display_name,
                vehicle_type_id=vehicle_type_id,
            )
            .on_conflict_do_nothing(index_elements=["fipe_id"])
        )

        self._session.execute(stmt)
        self._session.commit()

    def persist_manufacturers(
        self,
        manufacturers: fipe_schemas.FipeApiManufacturersResponseSchema,
        vehicle_type_id: int,
    ) -> None:
        for manufacturer in manufacturers.manufacturers:
            self.persist_manufacturer(manufacturer, vehicle_type_id)

    def persist_car_model(
        self,
        model: fipe_schemas.FipeApiModelSchema,
        manufacturer_id: str,
    ) -> None:
        stmt = (
            insert(db_models.Model)
            .values(
                fipe_id=model.code,
                display_name=model.display_name,
                manufacturer_id=manufacturer_id,
            )
            .on_conflict_do_nothing(index_elements=["fipe_id"])
        )

        self._session.execute(stmt)
        self._session.commit()

    def persist_car_models(
        self,
        models: fipe_schemas.FipeApiModelsResponseSchema,
        manufacturer_id: str,
    ) -> None:
        for model in models.car_models:
            self.persist_car_model(model, manufacturer_id)

    def persist_car_model_year(
        self,
        model_year: fipe_schemas.FipeApiModelYearSchema,
        model_id: str,
    ) -> None:
        year_str, fuel_type_str = model_year.display_name.split("-")

        stmt = (
            insert(db_models.ModelYear)
            .values(
                fipe_id=model_year.code,
                display_name=model_year.display_name,
                model_id=model_id,
                year=int(year_str.strip()),
                fuel_type=int(fuel_type_str.strip()),
            )
            .on_conflict_do_nothing(index_elements=["fipe_id", "model_id"])
        )

        self._session.execute(stmt)
        self._session.commit()

    def persist_car_model_years(
        self,
        model_years: fipe_schemas.FipeApiModelYearsResponseSchema,
        model_id: str,
    ) -> None:
        for model_year in model_years.car_model_years:
            self.persist_car_model_year(model_year, model_id)

    def persist_car_price(
        self,
        car_price: fipe_schemas.FipeApiCarPriceSchema,
        manufacturer_id: str,
        model_id: str,
        model_year_id: str,
        vehicle_type_id: int,
        reference_table_id: str,
    ) -> None:
        _reference_month = car_price.reference_month_name.strip()
        _value = convert_brl_str_to_float(car_price.value)
        _raw_data_json = json.dumps(car_price.raw_data)

        stmt = (
            insert(db_models.CarPrice)
            .values(
                # from args
                manufacturer_id=manufacturer_id,
                model_id=model_id,
                model_year_id=model_year_id,
                vehicle_type_id=vehicle_type_id,
                reference_table_id=reference_table_id,
                # from schema
                authentication=car_price.authentication,
                query_date=car_price.query_date,
                fipe_vehicle_code=car_price.fipe_vehicle_code,
                # converted from schema
                reference_month=_reference_month,
                value=_value,
                raw_data=_raw_data_json,
            )
            .on_conflict_do_update(
                index_elements=[
                    db_models.CarPrice.authentication,
                ],
                set_={
                    db_models.CarPrice.value: _value,
                    db_models.CarPrice.query_date: car_price.query_date,
                    db_models.CarPrice.reference_month: car_price.reference_month_name,
                },
            )
        )

        self._session.execute(stmt)
        self._session.commit()

    def get_latest_reference_table_id(self) -> str:
        ref_table_db = db_models.ReferenceTable()
        latest_ref_table = ref_table_db.get_latest_reference_table(self._session)

        return latest_ref_table.fipe_id
