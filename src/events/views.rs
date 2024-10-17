use crate::common::filter::{apply_filters, parse_range};
use crate::common::models::FilterOptions;
use crate::common::pagination::calculate_content_range;
use crate::common::sort::generic_sort;
use crate::events::db::Entity as EventDB;
use crate::events::models::{CreateEvent, Event, UpdateEvent};
use axum::response::IntoResponse;
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    routing, Json, Router,
};
use sea_orm::{prelude::*, query::*, ActiveModelTrait, Condition, DatabaseConnection, EntityTrait};
use sea_query::Expr;
use serde_json::json;
use uuid::Uuid;

const RESOURCE_NAME: &str = "events";

pub fn router(db: DatabaseConnection) -> Router {
    Router::new()
        .route("/", routing::get(get_all).post(create_one))
        .route(
            "/:id",
            routing::get(get_one_by_id)
                .delete(delete_one_by_id)
                .put(update_one_by_id),
        )
        .with_state(db)
}

#[utoipa::path(get, path = "/v1/events", responses((status = OK, body = PlotWithCoords)))]
pub async fn get_all(
    Query(params): Query<FilterOptions>,
    State(db): State<DatabaseConnection>,
) -> impl IntoResponse {
    let (offset, limit) = parse_range(params.range.clone());
    let condition: Condition = apply_filters(
        params.filter.clone(),
        &[
            ("title", super::db::Column::Title),
            ("description", super::db::Column::Description),
            ("start_time", super::db::Column::StartTime),
            ("end_time", super::db::Column::EndTime),
        ],
    );
    let (order_column, order_direction) = generic_sort(
        params.sort.clone(),
        &[
            ("id", super::db::Column::Id),
            ("description", super::db::Column::Description),
            ("title", super::db::Column::Title),
            ("start_time", super::db::Column::StartTime),
            ("end_time", super::db::Column::EndTime),
        ],
        super::db::Column::Id,
    );

    let objs = super::db::Entity::find()
        .filter(condition.clone())
        .order_by(order_column, order_direction)
        .offset(offset)
        .limit(limit)
        .all(&db)
        .await
        .unwrap();

    let response_objs: Vec<super::models::Event> = objs
        .into_iter()
        .map(|obj| super::models::Event::from(obj))
        .collect();

    let total_count: u64 = <super::db::Entity>::find()
        .filter(condition.clone())
        .count(&db)
        .await
        .unwrap_or(0);
    println!("Total count: {}", total_count);

    let headers = calculate_content_range(offset, limit, total_count, RESOURCE_NAME);

    (headers, Json(response_objs))
}

#[utoipa::path(post, path = "/v1/events", request_body = CreateEvent, responses((status = 201)))]
pub async fn create_one(
    State(db): State<DatabaseConnection>,
    Json(payload): Json<CreateEvent>,
) -> impl IntoResponse {
    // Create a new ActiveModel for the event
    println!("Payload: {:?}", payload);
    let new_event: super::db::ActiveModel = super::db::ActiveModel::from(payload);
    println!("New event: {:?}", new_event);
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
        .filter(Expr::col(super::db::Column::Id).eq(id))
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
        .filter(Expr::col(super::db::Column::Id).eq(id))
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
    let obj = super::db::Entity::find()
        .filter(super::db::Column::Id.eq(id))
        .one(&db)
        .await
        .unwrap();

    // If the event is not found, return a 404 response
    if obj.is_none() {
        return (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Event not found"})),
        )
            .into_response();
    }

    // Convert the UpdateEvent payload into an ActiveModel
    let active_model = payload.into_active_model(id);

    // Update the event in the database
    let updated_event: super::models::Event =
        super::models::Event::from(active_model.update(&db).await.unwrap());

    // Return the updated event
    (StatusCode::OK, Json(updated_event)).into_response()
}
