import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings


def test_add_photo(
    client: TestClient,
    db: Session,
    testimage
) -> None:
    pass
# 
#     person = {"first_names": "test_create_event1",
#               "last_names": "test_create_event1",
#               "email": "test_create_event1@gmail.com"}
# 
#     res_person = client.post(f"{settings.API_V1_STR}/persons", json=person)
#     assert res_person.status_code == 200, f"{res_person.json()}"
# 
#     event = {"title": 'Visit museum', 
#             "description": "Went to the museum for a few hours, saw a lot "
#                            "of paintings",
#             "start_time": "2022-01-14T07:00:00",
#             "end_time": "2022-01-14T09:00:00",
#             "owner": res_person.json().get('uuid')}
# 
    res = client.post(
        f"{settings.API_V1_STR}/photos", 
        files={"file": ('image.jpg', testimage, 'image/png')})
    assert res.json() == 0
#     assert 200 <= res.status_code < 300
#     created_event = res.json()
# 
#     assert created_event["title"] == event['title']
#     assert created_event["description"] == event['description']
#     assert created_event["start_time"] == event['start_time']
#     assert created_event["end_time"] == event['end_time']
#     
#     assert created_event["owner"]["first_names"] == person['first_names']
#     assert created_event["owner"]["last_names"] == person['last_names']
#     assert created_event["owner"]["email"] == person['email']
