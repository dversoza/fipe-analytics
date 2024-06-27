from providers.fipe.schemas import FipeApiReferenceTableResponseSchema


class TestFipeApiReferenceTableResponseSchema:
    sample_api_response = [
        {
            "Codigo": "123",
            "Mes": "janeiro/2021 ",
        },
        {
            "Codigo": "456",
            "Mes": "fevereiro/2021 ",
        },
    ]

    def test_model_loads_from_api_response(self):
        schema = FipeApiReferenceTableResponseSchema(
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
        schema = FipeApiReferenceTableResponseSchema(
            reference_tables=self.sample_api_response
        )
        assert schema.organize_by_year_month() == {
            2021: {
                1: "123",
                2: "456",
            }
        }
