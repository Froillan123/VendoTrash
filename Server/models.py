from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from db import Base


class User(Base):
    """User model for VendoTrash"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer", nullable=False)  # admin, customer
    is_active = Column(Boolean, default=True)
    total_points = Column(Integer, default=0)
    total_plastic = Column(Integer, default=0)
    total_metal = Column(Integer, default=0)
    total_transactions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    redemptions = relationship("Redemption", back_populates="user")


class Machine(Base):
    """Vending machine model"""
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="Online")  # Online, Offline, Maintenance
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    bin_capacity = Column(Integer, default=100)
    total_collected = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="machine")


class Transaction(Base):
    """Transaction model - tracks trash deposits"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    material_type = Column(String, nullable=False)  # PLASTIC, NON_PLASTIC
    points_earned = Column(Integer, nullable=False)
    status = Column(String, default="Completed")  # Completed, Pending, Failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    machine = relationship("Machine", back_populates="transactions")


class Reward(Base):
    """Reward catalog model"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    points_required = Column(Integer, nullable=False)
    category = Column(String, nullable=False)  # wifi, data, voucher
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    redemptions = relationship("Redemption", back_populates="reward")


class Redemption(Base):
    """Redemption model - tracks point redemptions"""
    __tablename__ = "redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    points_used = Column(Integer, nullable=False)
    status = Column(String, default="Completed")  # Completed, Pending, Failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="redemptions")
    reward = relationship("Reward", back_populates="redemptions")

