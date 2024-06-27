from pydantic import BaseModel, Field, ConfigDict

from providers.fipe.utils import convert_month_str_to_int


class FipeApiReferenceTableSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias="Codigo")
    display_name: str = Field(alias="Mes")


class FipeApiReferenceTablesResponseSchema(BaseModel):
    reference_tables: list[FipeApiReferenceTableSchema]

    def organize_by_year_month(self) -> dict[int, dict[int, str]]:
        """Organize the reference tables by year and month.

        Returns:
            dict[int, dict[int, str]]: A dictionary with the year as the key and a
                dictionary with the month as the key and the code as the value.
        """
        result = {}

        for reference_table in self.reference_tables:
            month_str, year_str = reference_table.display_name.split("/")

            year = int(year_str.strip())
            month = convert_month_str_to_int(month_str)

            if year not in result:
                result[year] = {}

            result[year][month] = reference_table.code

        return result


class FipeApiManufacturerSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias="Value")
    display_name: str = Field(alias="Label")


class FipeApiManufacturersResponseSchema(BaseModel):
    manufacturers: list[FipeApiManufacturerSchema]


class FipeApiCarModelSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str | int = Field(alias="Value")
    display_name: str = Field(alias="Label")


class FipeApiCarModelsResponseSchema(BaseModel):
    car_models: list[FipeApiCarModelSchema]


class FipeApiCarModelYearSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias="Value")
    display_name: str = Field(alias="Label")


class FipeApiCarModelYearsResponseSchema(BaseModel):
    car_model_years: list[FipeApiCarModelYearSchema]


class FipeApiCarPriceResponseSchema(BaseModel):
    """
    {
        "Valor": "R$ 125.383,00",
        "Marca": "Ford",
        "Modelo": "Fusion Titanium 2.0 GTDI Eco. Awd Aut.",
        "AnoModelo": 2019,
        "Combustivel": "Gasolina",
        "CodigoFipe": "003376-6",
        "MesReferencia": "junho de 2024 ",
        "Autenticacao": "g2bmp6342sc9z",
        "TipoVeiculo": 1,
        "SiglaCombustivel": "G",
        "DataConsulta": "quinta-feira, 27 de junho de 2024 13:24"
    }
    """

    model_config = ConfigDict(populate_by_name=True)

    value: str = Field(alias="Valor")
    manufacturer_name: str = Field(alias="Marca")
    car_model_name: str = Field(alias="Modelo")
    car_model_year: int = Field(alias="AnoModelo")
    fuel_type_name: str = Field(alias="Combustivel")
    fipe_vehicle_code: str = Field(alias="CodigoFipe")
    reference_month_name: str = Field(alias="MesReferencia")
    authentication: str = Field(alias="Autenticacao")
    vehicle_type_id: int = Field(alias="TipoVeiculo")
    fuel_type_code: str = Field(alias="SiglaCombustivel")
    query_date: str = Field(alias="DataConsulta")

    raw_data: dict = Field(alias="raw_data")
