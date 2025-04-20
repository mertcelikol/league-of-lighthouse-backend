from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# Define roles as an Enum
class UserRole(str, enum.Enum):
    student = "student"
    parent = "parent"
    teacher = "teacher"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), nullable=False)

    # If this user is a student, they can be related to parents/teachers
    student_data = relationship("StudentData", back_populates="student", uselist=False)

class StudentData(Base):
    __tablename__ = "student_data"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    data = Column(String)  # Replace with actual student data fields
    student = relationship("User", back_populates="student_data")
