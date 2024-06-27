from providers.fipe.schemas import (
    FipeApiReferenceTablesResponseSchema,
    FipeApiManufacturersResponseSchema,
    FipeApiModelsResponseSchema,
)


class TestFipeApiReferenceTableResponseSchema:
    sample_api_response = [
        {"Codigo": "123", "Mes": "janeiro/2021 "},
        {"Codigo": "456", "Mes": "fevereiro/2021 "},
    ]

    def test_model_loads_from_api_response(self):
        schema = FipeApiReferenceTablesResponseSchema(
            reference_tables=self.sample_api_response
        )
        assert schema.reference_tables[0].code == "123"
        assert schema.reference_tables[0].display_name == "janeiro/2021 "
        assert schema.reference_tables[1].code == "456"
        assert schema.reference_tables[1].display_name == "fevereiro/2021 "

        assert schema.model_dump() == {
            "reference_tables": [
                {"code": "123", "display_name": "janeiro/2021 "},
                {"code": "456", "display_name": "fevereiro/2021 "},
            ]
        }

    def test_organize_reference_tables_by_year_month(self):
        schema = FipeApiReferenceTablesResponseSchema(
            reference_tables=self.sample_api_response
        )
        assert schema.organize_by_year_month() == {
            2021: {
                1: "123",
                2: "456",
            }
        }


class TestFipeApiManufacturersResponseSchema:
    sample_api_response = [
        {"Value": "123", "Label": "Ford"},
        {"Value": "456", "Label": "Chevrolet"},
        {"Label": "Acura", "Value": "1"},
        {"Label": "Agrale", "Value": "2"},
    ]

    def test_model_loads_from_api_response(self):
        schema = FipeApiManufacturersResponseSchema(
            manufacturers=self.sample_api_response
        )

        assert schema.manufacturers[0].code == "123"
        assert schema.manufacturers[0].display_name == "Ford"
        assert schema.manufacturers[-1].code == "2"
        assert schema.manufacturers[-1].display_name == "Agrale"

        assert schema.model_dump() == {
            "manufacturers": [
                {"code": "123", "display_name": "Ford"},
                {"code": "456", "display_name": "Chevrolet"},
                {"code": "1", "display_name": "Acura"},
                {"code": "2", "display_name": "Agrale"},
            ]
        }


class TestFipeApiModelsResponseSchema:
    sample_api_response = [
        {"Value": "123", "Label": "Fiesta"},
        {"Value": "456", "Label": "Cruze"},
        {"Label": "A3", "Value": "1"},
        {"Label": "A4", "Value": "2"},
    ]

    def test_model_loads_from_api_response(self):
        schema = FipeApiModelsResponseSchema(car_models=self.sample_api_response)

        assert schema.car_models[0].code == "123"
        assert schema.car_models[0].display_name == "Fiesta"
        assert schema.car_models[-1].code == "2"
        assert schema.car_models[-1].display_name == "A4"

        assert schema.model_dump() == {
            "car_models": [
                {"code": "123", "display_name": "Fiesta"},
                {"code": "456", "display_name": "Cruze"},
                {"code": "1", "display_name": "A3"},
                {"code": "2", "display_name": "A4"},
            ]
        }
