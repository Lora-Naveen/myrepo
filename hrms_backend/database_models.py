
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

# Define the base class for SQLAlchemy models
Base = declarative_base()
dbURL = "sqlite:///project.db"
eng = create_engine(dbURL, echo=False) #Set echo=True for SQL logs

# Define the 'users' table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    roles = Column(String, nullable=False)  # Array of roles
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    token_version = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    employee = relationship("Employee", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    devices = relationship("Device", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', roles='{self.roles}')>"

# Define the 'employees' table
class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    employee_code = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    role = Column(String)
    date_of_joining = Column(Date, nullable=False)
    salary = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    payroll_records = relationship("Payroll", back_populates="employee")
    location_logs = relationship("LocationLog", back_populates="employee")

# Define the 'departments' table
class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    employees = relationship("Employee", back_populates="department")

# Define the 'attendance' table
class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    notes = Column(Text)

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

# Define the 'payroll' table
class Payroll(Base):
    __tablename__ = 'payroll'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float, nullable=False)
    generated_at = Column(DateTime, default=datetime.now)

    # Relationships
    employee = relationship("Employee", back_populates="payroll_records")

# Define the 'refresh_tokens' table
class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    jti = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    issued_at = Column(DateTime, default=datetime.now)
    revoked = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

# Define the 'devices' table
class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    device_id = Column(String, nullable=False)
    device_info = Column(JSON)
    ip_address = Column(String)
    last_login_at = Column(DateTime)
    last_logout_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="devices")

# Define the 'location_logs' table
class LocationLog(Base):
    __tablename__ = 'location_logs'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)
    source = Column(String, nullable=False)  # mobile/web

    # Relationships
    employee = relationship("Employee", back_populates="location_logs")

# Database setup
def create_database():
    Base.metadata.create_all(eng)
    SessionLocal = sessionmaker(bind=eng)

    return SessionLocal

def create_session(engine = eng):
    session = sessionmaker(bind = engine)
    db= session()
    return db

if __name__ == "__main__":
    # Create the database and tables
    create_database()
    print("Database and tables created successfully!")