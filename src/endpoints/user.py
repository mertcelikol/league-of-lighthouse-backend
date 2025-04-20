from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext

from ..database import get_db
from ..utils import APIException
from ..auth import get_current_user, require_role
from ..models import User

router = APIRouter()

# --- Serializers ---

class CreateUserSerializer(BaseModel):
    password: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True
    role: str  # should be "student", "parent", or "teacher"

class UserSmallSerializer(BaseModel):
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True

class UpdateStudentSerializer(BaseModel):
    is_active: bool


# --- Endpoints ---

# Get all users
@router.get("/user")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {
        "msg": "List of all users",
        "data": [UserSmallSerializer.model_validate(user) for user in users]
    }

# Get a single user (must exist)
@router.get("/user/{user_id}")
def read_single_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise APIException("User not found", status_code=404)
    return user.serialize()


# Create a new user
@router.post("/user")
def create_user(payload: CreateUserSerializer, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise APIException("User already exists with this email", status_code=400)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(payload.password)

    db_user = User(
        email=payload.email,
        is_active=payload.is_active,
        role=payload.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"msg": "User created", "user": UserSmallSerializer.model_validate(db_user)}


# --- Student & Parent specific access ---

# View student (parents and students)
@router.get("/student/{student_id}")
def view_student(student_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(require_role(["student", "parent"]))):

    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise APIException("Student not found", status_code=404)

    return UserSmallSerializer.model_validate(student)


# Edit student (teachers only)
@router.put("/student/{student_id}")
def edit_student(student_id: int,
                 payload: UpdateStudentSerializer,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(require_role(["teacher"]))):

    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise APIException("Student not found", status_code=404)

    student.is_active = payload.is_active
    db.commit()
    return {"msg": "Student updated successfully"}
