from fastapi import APIRouter, Depends, HTTPException, status

from app.database import delete_user, list_users
from app.models import Role, UserInDB, UserPublic
from app.security import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_own_profile(current_user: UserInDB = Depends(get_current_user)):
    """Any authenticated user can read their own profile."""
    return UserPublic(username=current_user.username, role=current_user.role)


@router.get("", response_model=list[UserPublic])
def list_all_users(_: UserInDB = Depends(require_role(Role.admin))):
    """Admin only: list every account."""
    return [UserPublic(username=u.username, role=u.role) for u in list_users()]


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(
    username: str,
    current_user: UserInDB = Depends(require_role(Role.admin)),
):
    """Admin only: delete an account. Admins cannot delete themselves."""
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    if not delete_user(username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
