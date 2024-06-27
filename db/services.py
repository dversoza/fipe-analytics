from db.models.all_models import CarModelYear, ReferenceTable, Manufacturer

from sqlalchemy.orm import Session


def list_reference_tables(db_session: Session, **kwargs) -> list[ReferenceTable]:
    reference_tables_qs = db_session.query(ReferenceTable)
    if year := kwargs.get("year"):
        reference_tables_qs = reference_tables_qs.filter(ReferenceTable.year == year)

    if year_gte := kwargs.get("year_gte"):
        reference_tables_qs = reference_tables_qs.filter(
            ReferenceTable.year >= year_gte
        )
        reference_tables_qs = reference_tables_qs.order_by(
            ReferenceTable.year.desc(), ReferenceTable.month.desc()
        )

    if year_lte := kwargs.get("year_lte"):
        reference_tables_qs = reference_tables_qs.filter(
            ReferenceTable.year <= year_lte
        )
        reference_tables_qs = reference_tables_qs.order_by(
            ReferenceTable.year, ReferenceTable.month
        )

    if month := kwargs.get("month"):
        reference_tables_qs = reference_tables_qs.filter(ReferenceTable.month == month)

    return reference_tables_qs.all()


def get_manufacturer_by_name(
    db_session: Session,
    name: str,
    vehicle_type_id: int = 1,
) -> Manufacturer:
    manufacturer_qs = db_session.query(Manufacturer)

    return manufacturer_qs.filter(
        Manufacturer.display_name == name,
        Manufacturer.vehicle_type_id == vehicle_type_id,
    ).first()


def list_car_models_years(
    db_session: Session,
    **kwargs,
) -> list[CarModelYear]:
    """Returns all car models that started being produced in the given year.

    Args:
        - db_session (Session): SQLAlchemy session.

    Returns:
        - list[CarModelYear]: List of car models years.
    """
    car_models_years_qs = db_session.query(CarModelYear)

    if year_gte := kwargs.get("year_gte"):
        car_models_years_qs = car_models_years_qs.filter(CarModelYear.year >= year_gte)

    return car_models_years_qs.all()


"""Cars must have a price for every month since the car was produced.

When the car starts being produced, it will receive the year `32000` in the
given reference table year

List all car model years
"""
