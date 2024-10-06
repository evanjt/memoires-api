use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "event")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: Uuid,
    pub title: Option<String>,
    pub description: Option<String>,
    pub start_time: DateTime,
    pub end_time: Option<DateTime>,
    pub created_on: DateTime,
    pub updated_on: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "crate::person::events::db::Entity")]
    PersonEvents,
}

impl Related<crate::person::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::PersonEvents.def()
    }
}

impl Related<crate::person::db::Entity> for Entity {
    fn to() -> RelationDef {
        crate::person::events::db::Relation::Person.def()
    }
    fn via() -> Option<RelationDef> {
        Some(crate::person::events::db::Relation::Event.def().rev())
    }
}

impl ActiveModelBehavior for ActiveModel {}
