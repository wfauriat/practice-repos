"""/items CRUD endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.db import SessionDep
from app.models import Item
from app.schemas import ItemCreate, ItemList, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemList)
def list_items(db: SessionDep, limit: int = 50, offset: int = 0) -> ItemList:
    if limit < 1 or limit > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "limit must be 1..200")
    if offset < 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "offset must be >= 0")

    total = db.scalar(select(func.count()).select_from(Item)) or 0
    rows = db.scalars(select(Item).order_by(Item.id).limit(limit).offset(offset)).all()
    return ItemList(
        items=[ItemRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: SessionDep) -> ItemRead:
    item = Item(name=payload.name, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemRead.model_validate(item)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: SessionDep) -> ItemRead:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found")
    return ItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: SessionDep) -> ItemRead:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: SessionDep) -> None:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found")
    db.delete(item)
    db.commit()
