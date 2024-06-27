from pydantic import BaseModel, Field, ConfigDict

from providers.fipe.utils import convert_month_str_to_int


class FipeApiReferenceTableSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias="Codigo")
    display_name: str = Field(alias="Mes")


class FipeApiReferenceTableResponseSchema(BaseModel):
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
