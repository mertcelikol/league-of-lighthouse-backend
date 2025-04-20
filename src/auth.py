from fastapi import Depends, HTTPException, status
from .models import User
from .database import get_db
from sqlalchemy.orm import Session

# Dummy function to get the current user (replace with actual auth logic)
def get_current_user(db: Session = Depends(get_db)) -> User:
    # For now, assume user with id 1 is logged in (mock)
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_role(required_roles: list[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Not authorized")
        return current_user
    return dependency
