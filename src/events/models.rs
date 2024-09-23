use chrono::NaiveDateTime;
use sea_orm::FromQueryResult;
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

#[derive(ToSchema, Serialize, Deserialize, FromQueryResult)]
pub struct Event {
    id: Uuid,
    title: Option<String>,
    description: Option<String>,
    start_time: Option<NaiveDateTime>,
    end_time: Option<NaiveDateTime>,
}

impl Event {
    pub fn from(obj: crate::events::db::Model) -> Self {
        Event {
            id: obj.uuid,
            title: obj.title,
            description: obj.description,
            start_time: obj.start_time,
            end_time: obj.end_time,
        }
    }
}

#[derive(ToSchema, Serialize, Deserialize)]
pub struct CreateEvent {
    pub owner_id: i32,
    pub title: Option<String>,
    pub description: Option<String>,
    pub start_time: Option<NaiveDateTime>,
    pub end_time: Option<NaiveDateTime>,
}

#[derive(ToSchema, Serialize, Deserialize)]
pub struct UpdateEvent {
    pub title: Option<String>,
    pub description: Option<String>,
    pub start_time: Option<NaiveDateTime>,
    pub end_time: Option<NaiveDateTime>,
}

#[cfg(test)]
use reqwest::Client;
use tokio;

#[tokio::test]
async fn test_get_all_events() {
    // Arrange: Create the HTTP client.
    let client = Client::new();

    // Act: Make the GET request to your API.
    let response = client
        .get("http://localhost:8000/events") // Adjust this to your actual endpoint
        .send()
        .await
        .expect("Failed to send request");

    // Assert: Check that the response is successful.
    assert!(
        &response.status().is_success(),
        "API call was not successful."
    );

    // Deserialize the response body into a Vec<Event>
    let events: Vec<Event> = response
        .json()
        .await
        .expect("Failed to deserialize response body.");

    // Check if you received any events back
    assert!(events.len() > 0, "No events found.");

    // Optionally: Check specific data for the first event.
    let first_event = &events[0];
    assert_eq!(first_event.title, Some("Expected event title".to_string())); // Change as needed
}
