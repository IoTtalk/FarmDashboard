from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()
models = ['AtPressure', 'CO2', 'Temperature', 'Humidity', 'WindSpeed', 'RainMeter', 'Bugs', 'UV1', 'UV2', 'UV3', 'Moisture1', 'PH1', 'Moisture2', 'PH2', 'Moisture3', 'PH3', 'Moisture4', 'PH4', 'Moisture5', 'PH5', 'Moisture6', 'PH6', 'Volt1', 'Volt2', 'Current1', 'Current2', 'Power1', 'Power2']

class AtPressure(base):
    __tablename__ = 'atpressure'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)


class CO2(base):
    __tablename__ = 'co2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Temperature(base):
    __tablename__ = 'temperature'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Humidity(base):
    __tablename__ = 'humidity'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class WindSpeed(base):
    __tablename__ = 'windspeed'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class RainMeter(base):
    __tablename__ = 'rainmeter'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Bugs(base):
    __tablename__ = 'bugs'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class UV1(base):
    __tablename__ = 'uv1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class UV2(base):
    __tablename__ = 'uv2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class UV3(base):
    __tablename__ = 'uv3'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Moisture1(base):
    __tablename__ = 'moisture1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class PH1(base):
    __tablename__ = 'ph1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Moisture2(base):
    __tablename__ = 'moisture2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class PH2(base):
    __tablename__ = 'ph2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Moisture3(base):
    __tablename__ = 'moisture3'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class PH3(base):
    __tablename__ = 'ph3'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class Moisture4(base):
    __tablename__ = 'moisture4'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


class PH4(base):
    __tablename__ = 'ph4'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Moisture5(base):
    __tablename__ = 'moisture5'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class PH5(base):
    __tablename__ = 'ph5'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Moisture6(base):
    __tablename__ = 'moisture6'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class PH6(base):
    __tablename__ = 'ph6'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Volt1(base):
    __tablename__ = 'volt1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Volt2(base):
    __tablename__ = 'volt2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Current1(base):
    __tablename__ = 'current1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Current2(base):
    __tablename__ = 'current2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Power1(base):
    __tablename__ = 'power1'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)

class Power2(base):
    __tablename__ = 'power2'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    field = Column(Integer, ForeignKey('field.id'), primary_key=True, nullable=False)
    value = Column(Float)
    __table_args__ = (UniqueConstraint('field',
                                       'timestamp',
                                       name='UC_field_time'),)


####################################################

class user(base):
    __tablename__ = 'user'
    id = Column(Integer,
                primary_key=True,
                nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)


class field(base):
    __tablename__ = 'field'
    id = Column(Integer,
                primary_key=True,
                nullable=False)
    name = Column(String(50))
    alias = Column(String(50))


class sensor(base):
    __tablename__ = 'sensor'
    id = Column(Integer,
                primary_key=True,
                nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    df_name = Column(String(50), nullable=False, unique=True)
    alias = Column(String(50), nullable=False)
    unit = Column(String(50), default='')
    icon = Column(String(50), default='')
    bg_color = Column(String(50), default='bg-aqua')


class field_sensor(base):
    __tablename__ = 'field_sensor'
    id = Column(Integer,
                primary_key=True,
                nullable=False)
    field = Column(Integer,
                   ForeignKey('field.id'),
                   nullable=False)
    sensor = Column(Integer,
                    ForeignKey('sensor.id'),
                    nullable=False)
    df_name = Column(String(50), nullable=False)
    alias = Column(String(50), nullable=False)
    unit = Column(String(50), default='')
    icon = Column(String(50), default='')
    bg_color = Column(String(50), default='bg-aqua')
    __table_args__ = (UniqueConstraint('field',
                                       'df_name',
                                       name='UC_field_df_name'),)


class user_access(base):
    __tablename__ = 'user_access'
    id = Column(Integer,
                primary_key=True,
                nullable=False)
    user = Column(Integer,
                  ForeignKey('user.id'),
                  nullable=False)
    field = Column(Integer,
                   ForeignKey('field.id'),
                   nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
