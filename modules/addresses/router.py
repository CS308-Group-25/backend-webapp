from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.addresses.repository import AddressRepository
from modules.addresses.schema import AddressCreate, AddressResponse
from modules.auth.model import User

router = APIRouter(prefix="/api/v1/addresses", tags=["addresses"])


@router.get("", response_model=list[AddressResponse])
def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AddressRepository(db).get_by_user(current_user.id)


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AddressRepository(db).create(current_user.id, data)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = AddressRepository(db).delete(address_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")
