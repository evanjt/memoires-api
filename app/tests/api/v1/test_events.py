from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
#from app.tests.utils.item import create_random_item


def test_create_event(
    client: TestClient,
    #superuser_token_headers: dict,
    db: Session
) -> None:

    person = {"first_names": "test_create_event1",
              "last_names": "test_create_event1",
              "email": "test_create_event1@gmail.com"}

    res_person = client.post(f"{settings.API_V1_STR}/persons", json=person)
    assert res_person.status_code == 200, f"{res_person.json()}"

    event = {"title": 'Visit museum', 
            "description": "Went to the museum for a few hours, saw a lot "
                           "of paintings",
            "start_time": "2022-01-14T07:00:00",
            "end_time": "2022-01-14T09:00:00",
            "owner": res_person.json().get('uuid')}

    res = client.post(f"{settings.API_V1_STR}/events", json=event)
    assert 200 <= res.status_code < 300
    created_event = res.json()

    assert created_event["title"] == event['title']
    assert created_event["description"] == event['description']
    assert created_event["start_time"] == event['start_time']
    assert created_event["end_time"] == event['end_time']
    
    assert created_event["owner"]["first_names"] == person['first_names']
    assert created_event["owner"]["last_names"] == person['last_names']
    assert created_event["owner"]["email"] == person['email']
    
    #user = crud.person.get_by_email(db, email=username)
    #assert user
    #assert user.email == created_user["email"]
    
#def test_create_event(
    #client: TestClient,
    ##uperuser_token_headers: dict,
    #db: Session
#) -> None:
    #data = {"title": "Foo",
            #"description": "Fighters"}
    #response = client.post(
        #f"{settings.API_V1_STR}/events",
        ##headers=superuser_token_headers,
        #json=data,
    #)
    #assert response.status_code == 200
    #content = response.json()

    #assert content["title"] == data["title"]
    #assert content["description"] == data["description"]
    #assert "id" in content
    #assert "owner_id" in content


#def test_read_item(
    #client: TestClient, superuser_token_headers: dict, db: Session
#) -> None:
    #item = create_random_item(db)
    #response = client.get(
        #f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers,
    #)
    #assert response.status_code == 200
    #content = response.json()
    #assert content["title"] == item.title
    #assert content["description"] == item.description
    #assert content["id"] == item.id
    #assert content["owner_id"] == item.owner_id
