from fastapi import APIRouter, Depends, HTTPException, status

from app.database import delete_user, list_users
from app.models import Role, UserInDB, UserPublic
from app.security import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_own_profile(current_user: UserInDB = Depends(get_current_user)):
    """Alle innloggede brukere kan lese sin egen profil."""
    return UserPublic(username=current_user.username, role=current_user.role)


@router.get("", response_model=list[UserPublic])
def list_all_users(_: UserInDB = Depends(require_role(Role.admin))):
    """Bare admin: list opp alle kontoer."""
    return [UserPublic(username=u.username, role=u.role) for u in list_users()]


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(
    username: str,
    current_user: UserInDB = Depends(require_role(Role.admin)),
):
    """Bare admin: slett en konto. En admin kan ikke slette seg selv."""
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du kan ikke slette din egen konto",
        )
    if not delete_user(username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fant ikke brukeren",
        )
