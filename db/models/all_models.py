"""Database models for the reference tables."""

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, SmallInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm import Session
from db.models.base import SQLAlchemyDeclarativeBase


class ReferenceTable(SQLAlchemyDeclarativeBase):
    """Reference tables for the car price data."""

    __tablename__ = "tabela_referencia"

    fipe_id: Mapped[str] = mapped_column("fipe_id", String(10), primary_key=True)
    display_name: Mapped[str] = mapped_column("display_name", String(255))
    month: Mapped[int] = mapped_column("mes", Integer)
    year: Mapped[int] = mapped_column("ano", Integer)

    def get_latest_reference_table(self, session: Session) -> "ReferenceTable":
        return (
            session.query(ReferenceTable)
            .order_by(
                ReferenceTable.year.desc(),
                ReferenceTable.month.desc(),
            )
            .first()
        )


class Manufacturer(SQLAlchemyDeclarativeBase):
    """Car manufacturers."""

    __tablename__ = "marca"

    fipe_id: Mapped[str] = mapped_column("fipe_id", String(10), primary_key=True)
    display_name: Mapped[str] = mapped_column("display_name", String(255))
    vehicle_type_id: Mapped[int] = mapped_column("tipo_veiculo", SmallInteger)

    models = relationship("CarModel", back_populates="manufacturer")


class CarModel(SQLAlchemyDeclarativeBase):
    """Car models."""

    __tablename__ = "modelo"

    fipe_id: Mapped[str] = mapped_column("fipe_id", String(10), primary_key=True)
    display_name: Mapped[str] = mapped_column("display_name", String(255))
    manufacturer_id: Mapped[str] = mapped_column(
        "marca_id", String(10), ForeignKey("marca.fipe_id")
    )

    manufacturer = relationship("Manufacturer", back_populates="models", lazy="joined")
    model_years = relationship("CarModelYear", back_populates="car_model")


class CarModelYear(SQLAlchemyDeclarativeBase):
    """Car model years."""

    __tablename__ = "ano_modelo"

    fipe_id: Mapped[str] = mapped_column("fipe_id", String(10), primary_key=True)
    model_id: Mapped[str] = mapped_column(
        "modelo_id", String(10), ForeignKey("modelo.fipe_id")
    )
    display_name: Mapped[str] = mapped_column("display_name", String(255))
    year: Mapped[int] = mapped_column("ano", Integer)
    fuel_type: Mapped[int] = mapped_column("tipo_combustivel", Integer)

    car_model = relationship("CarModel", back_populates="model_years", lazy="joined")


class CarPrice(SQLAlchemyDeclarativeBase):
    """Car prices."""

    __tablename__ = "preco"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    manufacturer_id: Mapped[str] = mapped_column(
        "marca_id", String(10), ForeignKey("marca.fipe_id")
    )
    model_id: Mapped[str] = mapped_column(
        "modelo_id", String(10), ForeignKey("modelo.fipe_id")
    )
    model_year_id: Mapped[str] = mapped_column(
        "ano_modelo_id", String(10), ForeignKey("ano_modelo.fipe_id")
    )
    vehicle_type_id: Mapped[int] = mapped_column("codigo_tipo_veiculo", Integer)
    reference_table_id: Mapped[str] = mapped_column(
        "codigo_tabela_referencia", String(10), ForeignKey("tabela_referencia.fipe_id")
    )
    authentication: Mapped[str] = mapped_column("autenticacao", String(255))
    query_date: Mapped[str] = mapped_column("data_consulta", String(255))
    reference_month: Mapped[str] = mapped_column("mes_referencia", String(255))
    fipe_vehicle_code: Mapped[str] = mapped_column("codigo_fipe_veiculo", String(10))
    value: Mapped[float] = mapped_column("valor", Float)
    raw_data: Mapped[dict] = mapped_column("raw_data", JSON)

    manufacturer = relationship("Manufacturer")
    model = relationship("CarModel")
    model_year = relationship("CarModelYear")
    reference_table = relationship("ReferenceTable")


__all__ = ["ReferenceTable", "Manufacturer", "CarModel", "CarModelYear", "CarPrice"]
