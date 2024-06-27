"""Database models for the reference tables."""

from sqlalchemy import JSON, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.models.base import SQLAlchemyDeclarativeBase


class ReferenceTable(SQLAlchemyDeclarativeBase):
    """Reference tables for the car price data."""

    __tablename__ = "tabela_referencia"

    fipe_id = Column(String(10), primary_key=True)
    display_name = Column(String(255))
    month = Column("mes", Integer)
    year = Column("ano", Integer)


class Manufacturer(SQLAlchemyDeclarativeBase):
    """Car manufacturers."""

    __tablename__ = "marca"

    fipe_id = Column(String(10), primary_key=True)
    display_name = Column(String(255))

    models = relationship("Model", back_populates="manufacturer")


class Model(SQLAlchemyDeclarativeBase):
    """Car models."""

    __tablename__ = "modelo"

    fipe_id = Column(String(10), primary_key=True)
    manufacturer_id = Column(String(10), ForeignKey("marca.fipe_id"))
    display_name = Column(String(255))
    vehicle_type = Column("tipo_veiculo", Integer)

    manufacturer = relationship("Manufacturer", back_populates="models")


class ModelYear(SQLAlchemyDeclarativeBase):
    """Car model years."""

    __tablename__ = "ano_modelo"

    model_id = Column(String(10), ForeignKey("modelo.fipe_id"), primary_key=True)
    fipe_id = Column(String(10), primary_key=True)
    year = Column("ano", Integer)
    fuel_type = Column("tipo_combustivel", Integer)
    display_name = Column(String(255))

    model = relationship("Model")


class Price(SQLAlchemyDeclarativeBase):
    """Car prices."""

    __tablename__ = "preco"

    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(String(10), ForeignKey("marca.fipe_id"))
    model_id = Column(String(10), ForeignKey("modelo.fipe_id"))
    model_year_id = Column(String(10), ForeignKey("ano_modelo.fipe_id"))
    vehicle_type_code = Column("codigo_tipo_veiculo", Integer)
    reference_table_code = Column(
        "codigo_tabela_referencia", String(10), ForeignKey("tabela_referencia.fipe_id")
    )
    authentication = Column("autenticacao", String(255), unique=True)
    query_date = Column("data_consulta", String(255))
    reference_month = Column("mes_referencia", String(255))
    value = Column("valor", Float)
    fipe_vehicle_code = Column("codigo_fipe_veiculo", String(10))
    raw_data = Column("raw_data", JSON)

    manufacturer = relationship("Manufacturer")
    model = relationship("Model")
    model_year = relationship("ModelYear")
    reference_table = relationship("ReferenceTable")


__all__ = ["ReferenceTable", "Manufacturer", "Model", "ModelYear", "Price"]
