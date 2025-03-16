use chrono::{DateTime, Utc};
use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "event")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: Uuid,
    pub title: Option<String>,
    pub description: Option<String>,
    pub start_time: DateTime<Utc>,
    pub end_time: Option<DateTime<Utc>>,
    pub created_on: DateTime<Utc>,
    pub updated_on: DateTime<Utc>,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "crate::routes::person::events::db::Entity")]
    PersonEvents,
}

impl Related<crate::routes::person::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::PersonEvents.def()
    }
}

impl Related<crate::routes::person::db::Entity> for Entity {
    fn to() -> RelationDef {
        crate::routes::person::events::db::Relation::Person.def()
    }
    fn via() -> Option<RelationDef> {
        Some(
            crate::routes::person::events::db::Relation::Event
                .def()
                .rev(),
        )
    }
}

impl ActiveModelBehavior for ActiveModel {}
