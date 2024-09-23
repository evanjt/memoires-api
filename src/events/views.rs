use crate::common::models::FilterOptions;
use crate::events::db::ActiveModel as EventActiveModel;
use crate::events::db::Entity as EventDB;
use crate::events::models::Event;
use crate::events::models::{CreateEvent, UpdateEvent};
use axum::response::IntoResponse;
use axum::{extract::Path, http::StatusCode};
use axum::{extract::Query, http::header::HeaderMap, routing, Router};
use axum::{extract::State, Json};
use sea_orm::prelude::*;
use sea_orm::Condition;
use sea_orm::EntityTrait;
use sea_orm::{query::*, DatabaseConnection};
use sea_orm::{ActiveModelTrait, Set};
use sea_query::{Alias, Expr};
use serde_json::json;
use std::collections::HashMap;
use uuid::Uuid;

pub fn router(db: DatabaseConnection) -> Router {
    Router::new()
        .route("/", routing::get(get_all))
        .route("/", routing::post(create_one))
        .route("/:id", routing::get(get_one_by_id))
        .route("/:id", routing::delete(delete_one_by_id))
        .route("/:id", routing::put(update_one_by_id))
        .with_state(db)
}

#[utoipa::path(get, path = "/v1/events", responses((status = OK, body = PlotWithCoords)))]
pub async fn get_all(
    Query(params): Query<FilterOptions>,
    State(db): State<DatabaseConnection>,
) -> impl IntoResponse {
    // Default values for range and sorting
    let default_sort_column = "id";
    let default_sort_order = "ASC";

    // 1. Parse the filter, range, and sort parameters
    let filters: HashMap<String, String> = if let Some(filter) = params.filter {
        serde_json::from_str(&filter).unwrap_or_default()
    } else {
        HashMap::new()
    };

    let (offset, limit) = if let Some(range) = params.range {
        let range_vec: Vec<u64> = serde_json::from_str(&range).unwrap_or(vec![0, 24]); // Default to [0, 24]
        let start = range_vec.get(0).copied().unwrap_or(0);
        let end = range_vec.get(1).copied().unwrap_or(24);
        let limit = end - start + 1;
        (start, limit) // Offset is `start`, limit is the number of documents to fetch
    } else {
        (0, 25) // Default to 25 documents starting at 0
    };

    let (sort_column, sort_order) = if let Some(sort) = params.sort {
        let sort_vec: Vec<String> = serde_json::from_str(&sort).unwrap_or(vec![
            default_sort_column.to_string(),
            default_sort_order.to_string(),
        ]);
        (
            sort_vec
                .get(0)
                .cloned()
                .unwrap_or(default_sort_column.to_string()),
            sort_vec
                .get(1)
                .cloned()
                .unwrap_or(default_sort_order.to_string()),
        )
    } else {
        (
            default_sort_column.to_string(),
            default_sort_order.to_string(),
        )
    };

    // Apply filters
    let mut condition = Condition::all();
    for (key, mut value) in filters {
        value = value.trim().to_string();

        // Check if the value is a valid UUID
        if let Ok(uuid) = Uuid::parse_str(&value) {
            // If the value is a valid UUID, filter it as a UUID
            condition = condition.add(Expr::col(Alias::new(&key)).eq(uuid));
        } else {
            // Otherwise, treat it as a regular string filter
            condition = condition.add(Expr::col(Alias::new(&key)).eq(value));
        }
    }

    // Query with filtering, sorting, and pagination
    let order_direction = if sort_order == "ASC" {
        Order::Asc
    } else {
        Order::Desc
    };
    let order_column = match sort_column.as_str() {
        "id" => <EventDB as sea_orm::EntityTrait>::Column::Uuid,
        "description" => <EventDB as sea_orm::EntityTrait>::Column::Description,
        "title" => <EventDB as sea_orm::EntityTrait>::Column::Title,
        "start_time" => <EventDB as sea_orm::EntityTrait>::Column::StartTime,
        "end_time" => <EventDB as sea_orm::EntityTrait>::Column::EndTime,
        _ => <EventDB as sea_orm::EntityTrait>::Column::Id,
    };

    let objs = EventDB::find()
        .filter(condition)
        .order_by(order_column, order_direction)
        .offset(offset)
        .limit(limit)
        .all(&db)
        .await
        .unwrap();

    let events: Vec<Event> = objs
        .iter()
        .map(|event| Event::from(event.clone()))
        .collect::<Vec<Event>>();

    let total_count: u64 = EventDB::find().count(&db).await.unwrap();
    let max_offset_limit = (offset + limit - 1).min(total_count);
    println!(
        "Total count: {}, max offset limit: {}, offset: {}, limit: {}",
        total_count, max_offset_limit, offset, limit
    );
    let content_range = format!("events {}-{}/{}", offset, max_offset_limit, total_count);

    // Return the Content-Range as a header
    let mut headers = HeaderMap::new();
    headers.insert("Content-Range", content_range.parse().unwrap());
    (headers, Json(json!(events)))
}

#[utoipa::path(post, path = "/v1/events", request_body = CreateEvent, responses((status = 201)))]
pub async fn create_one(
    State(db): State<DatabaseConnection>,
    Json(payload): Json<CreateEvent>,
) -> impl IntoResponse {
    // Create a new ActiveModel for the event
    let new_event = EventActiveModel {
        uuid: Set(Uuid::new_v4()), // Generate a new UUID for the event
        owner_id: Set(payload.owner_id),
        title: Set(payload.title),
        description: Set(payload.description),
        start_time: Set(payload.start_time),
        end_time: Set(payload.end_time),
        ..Default::default()
    };

    // Insert the new event into the database
    match new_event.insert(&db).await {
        Ok(event) => (StatusCode::CREATED, Json(Event::from(event))).into_response(),
        Err(err) => {
            eprintln!("Failed to insert event: {:?}", err);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Failed to create event"})),
            )
                .into_response()
        }
    }
}
#[utoipa::path(get, path = "/v1/events/{id}", responses((status = 200, body = Event), (status = 404)))]
pub async fn get_one_by_id(
    Path(id): Path<Uuid>,
    State(db): State<DatabaseConnection>,
) -> impl IntoResponse {
    // Query the database for an event by UUID
    match EventDB::find()
        .filter(Expr::col(super::db::Column::Uuid).eq(id))
        .one(&db)
        .await
    {
        Ok(Some(event)) => {
            println!("Found event: {:?}", event);
            (StatusCode::OK, Json(Event::from(event))).into_response()
        }
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Event not found"})),
        )
            .into_response(),
        Err(err) => {
            eprintln!("Database query error: {:?}", err);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Internal Server Error"})),
            )
                .into_response()
        }
    }
}

#[utoipa::path(delete, path = "/v1/events/{id}", responses((status = 204), (status = 404)))]
pub async fn delete_one_by_id(
    Path(id): Path<Uuid>,
    State(db): State<DatabaseConnection>,
) -> impl IntoResponse {
    // Attempt to find the event by UUID
    match EventDB::find()
        .filter(Expr::col(super::db::Column::Uuid).eq(id))
        .one(&db)
        .await
    {
        Ok(Some(event)) => {
            // Delete the event if found
            let result = event.delete(&db).await;
            match result {
                Ok(_) => StatusCode::NO_CONTENT.into_response(), // Return 204 No Content
                Err(err) => {
                    eprintln!("Failed to delete event: {:?}", err);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(json!({"error": "Failed to delete event"})),
                    )
                        .into_response()
                }
            }
        }
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Event not found"})),
        )
            .into_response(),
        Err(err) => {
            eprintln!("Database query error: {:?}", err);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Internal Server Error"})),
            )
                .into_response()
        }
    }
}

#[utoipa::path(put, path = "/v1/events/{id}", request_body = UpdateEvent, responses((status = 200, body = Event), (status = 404)))]
pub async fn update_one_by_id(
    Path(id): Path<Uuid>,
    State(db): State<DatabaseConnection>,
    Json(payload): Json<UpdateEvent>,
) -> impl IntoResponse {
    // Find the event by UUID
    match EventDB::find()
        .filter(Expr::col(super::db::Column::Uuid).eq(id))
        .one(&db)
        .await
    {
        Ok(Some(event)) => {
            // Convert the found event into an ActiveModel for updating
            let mut active_event: EventActiveModel = event.into();

            // Apply updates from the incoming payload (if they exist)
            if let Some(title) = payload.title {
                active_event.title = Set(Some(title));
            }
            if let Some(description) = payload.description {
                active_event.description = Set(Some(description));
            }
            if let Some(start_time) = payload.start_time {
                active_event.start_time = Set(Some(start_time));
            }
            if let Some(end_time) = payload.end_time {
                active_event.end_time = Set(Some(end_time));
            }

            // Save the updated event back to the database
            match active_event.update(&db).await {
                Ok(updated_event) => {
                    (StatusCode::OK, Json(Event::from(updated_event))).into_response()
                }
                Err(err) => {
                    eprintln!("Failed to update event: {:?}", err);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(json!({"error": "Failed to update event"})),
                    )
                        .into_response()
                }
            }
        }
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Event not found"})),
        )
            .into_response(),
        Err(err) => {
            eprintln!("Database query error: {:?}", err);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Internal Server Error"})),
            )
                .into_response()
        }
    }
}
