from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        JSON, Float, Boolean, Text)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")          # analyst | admin
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False,
                           cascade="all, delete-orphan")
    scans = relationship("WebsiteScan", back_populates="user",
                         cascade="all, delete-orphan")
    saved = relationship("SavedWebsite", back_populates="user",
                        cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    user = relationship("User", back_populates="profile")


class WebsiteScan(Base):
    __tablename__ = "website_scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String, nullable=False)          # host
    full_url = Column(String, nullable=False)
    score = Column(Integer, default=0)
    risk_level = Column(String)                   # Very Low..Critical
    result = Column(JSON)                         # full analysis blob
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    findings = relationship("SecurityFinding", back_populates="scan",
                            cascade="all, delete-orphan")
    report = relationship("Report", back_populates="scan", uselist=False,
                          cascade="all, delete-orphan")


class SecurityFinding(Base):
    __tablename__ = "security_findings"
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("website_scans.id"))
    category = Column(String)          # SSL/TLS, Headers, DNS...
    title = Column(String)
    status = Column(String)            # pass | fail | info
    detail = Column(Text)
    severity = Column(String, default="info")   # info|low|medium|high|critical
    scan = relationship("WebsiteScan", back_populates="findings")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("website_scans.id"))
    format = Column(String)            # pdf | html
    generated_at = Column(DateTime, default=datetime.utcnow)
    scan = relationship("WebsiteScan", back_populates="report")


class SavedWebsite(Base):
    __tablename__ = "saved_websites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="saved")


class AdminLog(Base):
    __tablename__ = "admin_logs"
    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    target = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)