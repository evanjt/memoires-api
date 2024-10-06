use chrono::NaiveDateTime;
use sea_orm::{FromQueryResult, NotSet, Set};
use serde::de::DeserializeOwned;
use serde::de::Deserializer;
use serde::{Deserialize, Serialize};
use serde_with::rust::double_option;
use utoipa::ToSchema;
use uuid::Uuid;

#[derive(ToSchema, Serialize, Deserialize, FromQueryResult)]
pub struct Event {
    id: Uuid,
    title: Option<String>,
    description: Option<String>,
    start_time: NaiveDateTime,
    end_time: Option<NaiveDateTime>,
}

impl Event {
    pub fn from(obj: crate::events::db::Model) -> Self {
        Event {
            id: obj.id,
            title: obj.title,
            description: obj.description,
            start_time: obj.start_time,
            end_time: obj.end_time,
        }
    }
}

#[derive(ToSchema, Serialize, Deserialize)]
pub struct CreateEvent {
    pub title: Option<String>,
    pub description: Option<String>,
    pub start_time: NaiveDateTime,
    pub end_time: Option<NaiveDateTime>,
}

impl From<CreateEvent> for super::db::ActiveModel {
    fn from(obj: CreateEvent) -> Self {
        super::db::ActiveModel {
            id: Set(Uuid::new_v4()),
            title: Set(obj.title),
            description: Set(obj.description),
            start_time: Set(obj.start_time),
            end_time: Set(obj.end_time),
            created_on: Set(chrono::Utc::now().naive_utc()),
            updated_on: Set(chrono::Utc::now().naive_utc()),
        }
    }
}

#[derive(ToSchema, Serialize, Deserialize)]
pub struct UpdateEvent {
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        with = "::serde_with::rust::double_option"
    )]
    pub title: Option<Option<String>>,
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        with = "::serde_with::rust::double_option"
    )]
    pub description: Option<Option<String>>,
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        with = "::serde_with::rust::double_option"
    )]
    pub start_time: Option<Option<NaiveDateTime>>,
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        with = "::serde_with::rust::double_option"
    )]
    pub end_time: Option<Option<NaiveDateTime>>,
}
impl UpdateEvent {
    pub fn into_active_model(self, id: Uuid) -> super::db::ActiveModel {
        // Apply updates from the incoming payload (if they exist). A
        // double option field is used to allow for the possibility of setting
        // a field to None. If it is None, it's missing (not to be updated),
        // if it's Some(None), it's to be set to None, and if it's Some(Some(value)),
        // it's to be updated to that value.

        super::db::ActiveModel {
            id: Set(id),
            title: match self.title {
                Some(Some(title)) => Set(Some(title)),
                Some(None) => Set(None),
                None => NotSet,
            },
            description: match self.description {
                Some(Some(description)) => Set(Some(description)),
                Some(None) => Set(None),
                None => NotSet,
            },
            start_time: match self.start_time {
                Some(Some(start_time)) => Set(start_time),
                Some(None) => NotSet, // Cannot set to None
                None => NotSet,
            },
            end_time: match self.end_time {
                Some(Some(value)) => Set(Some(value)),
                Some(None) => Set(None),
                None => NotSet,
            },
            created_on: NotSet,
            updated_on: Set(chrono::Utc::now().naive_utc()),
        }
    }
}

impl From<super::db::Model> for Event {
    fn from(obj: super::db::Model) -> Self {
        Event {
            id: obj.id,
            title: obj.title,
            description: obj.description,
            start_time: obj.start_time,
            end_time: obj.end_time,
        }
    }
}
