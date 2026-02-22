# models.py
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from database import Base
from datetime import datetime

class Load(Base):
    __tablename__ = 'loads'
    id = Column(Integer, primary_key=True)
    load_id = Column(String(20), unique=True, nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    pickup_datetime = Column(TIMESTAMP, nullable=False)
    delivery_datetime = Column(TIMESTAMP, nullable=False)
    equipment_type = Column(String(50), nullable=False)
    loadboard_rate = Column(DECIMAL(10,2), nullable=False)
    true_cost = Column(DECIMAL(10,2))
    notes = Column(String)
    weight = Column(Integer)
    commodity_type = Column(String(100))
    num_of_pieces = Column(Integer)
    miles = Column(Integer)
    dimensions = Column(String(50))
    status = Column(String(20), default='available')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Call(Base):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    call_id = Column(String(50), unique=True, nullable=False)
    mc_number = Column(String(20))
    carrier_name = Column(String(255))
    caller_name = Column(String(100))
    duration_seconds = Column(Integer)
    outcome = Column(String(50))
    sentiment = Column(String(20))
    negotiation_rounds = Column(Integer, default=0)
    transcription = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    call_id = Column(String(50), ForeignKey('calls.call_id'))
    load_id = Column(String(20), ForeignKey('loads.load_id'))
    mc_number = Column(String(20), nullable=False)
    agreed_rate = Column(DECIMAL(10,2), nullable=False)
    loadboard_rate = Column(DECIMAL(10,2), nullable=False)
    margin_percentage = Column(DECIMAL(5,2))
    negotiation_rounds = Column(Integer, default=0)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    origin_lat = Column(DECIMAL(9,6))
    origin_lng = Column(DECIMAL(9,6))
    destination_lat = Column(DECIMAL(9,6))
    destination_lng = Column(DECIMAL(9,6))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)