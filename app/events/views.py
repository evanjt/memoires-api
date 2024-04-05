from fastapi import Depends, APIRouter, Query, Response, Body, HTTPException
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.events.models import (
    Event,
    EventCreate,
    EventRead,
    EventUpdate,
)
from uuid import UUID
from sqlalchemy import func
import json


router = APIRouter()


@router.get("/{event_id}", response_model=EventRead)
async def get_event(
    session: AsyncSession = Depends(get_session),
    *,
    event_id: UUID,
) -> EventRead:
    """Get a event by id"""
    res = await session.execute(select(Event).where(Event.id == event_id))
    event = res.scalars().one_or_none()

    return event


@router.get("", response_model=list[EventRead])
async def get_events(
    response: Response,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Get all events"""

    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    query = select(Event)

    # Do a query to satisfy total count for "Content-Range" header
    count_query = select(func.count(Event.iterator))
    if len(filter):  # Have to filter twice for some reason? SQLModel state?
        for field, value in filter.items():
            for qry in [query, count_query]:  # Apply filter to both queries
                if isinstance(value, list):
                    qry = qry.where(getattr(Event, field).in_(value))
                elif field == "id":
                    qry = qry.where(getattr(Event, field) == value)
                else:
                    qry = qry.where(getattr(Event, field).like(f"%{value}%"))

    # Execute total count query (including filter)
    total_count_query = await session.execute(count_query)
    total_count = total_count_query.scalar_one()

    # Order by sort field params ie. ["name","ASC"]
    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(getattr(Event, sort_field))
        else:
            query = query.order_by(getattr(Event, sort_field).desc())

    # Filter by filter field params ie. {"name":"bar"}
    if len(filter):
        for field, value in filter.items():
            if isinstance(value, list):
                query = query.where(getattr(Event, field).in_(value))
            elif field == "id":
                query = query.where(getattr(Event, field) == value)
            else:
                query = query.where(getattr(Event, field).like(f"%{value}%"))

    if len(range) == 2:
        start, end = range
        query = query.offset(start).limit(end - start + 1)
    else:
        start, end = [0, total_count]  # For content-range header

    # Execute query
    results = await session.execute(query)
    events = results.scalars().all()

    response.headers["Content-Range"] = f"events {start}-{end}/{total_count}"

    return events


@router.post("", response_model=EventRead)
async def create_event(
    event: EventCreate = Body(...),
    session: AsyncSession = Depends(get_session),
) -> EventRead:
    """Creates a event"""
    print(event)
    event = Event.from_orm(event)
    session.add(event)
    await session.commit()
    await session.refresh(event)

    return event


@router.put("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: UUID,
    event_update: EventUpdate,
    session: AsyncSession = Depends(get_session),
) -> EventRead:
    res = await session.execute(select(Event).where(Event.id == event_id))
    event_db = res.scalars().one()
    event_data = event_update.dict(exclude_unset=True)

    if not event_db:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update the fields from the request
    for field, value in event_data.items():
        print(f"Updating: {field}, {value}")
        setattr(event_db, field, value)

    session.add(event_db)
    await session.commit()
    await session.refresh(event_db)

    return event_db


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
    filter: dict[str, str] | None = None,
) -> None:
    """Delete a event by id"""
    res = await session.execute(select(Event).where(Event.id == event_id))
    event = res.scalars().one_or_none()

    if event:
        await session.delete(event)
        await session.commit()
