//! `SeaORM` Entity, @generated by sea-orm-codegen 1.0.1

use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "person_events")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id_person: i32,
    #[sea_orm(primary_key, auto_increment = false)]
    pub id_event: i32,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "crate::events::db::Entity",
        from = "Column::IdEvent",
        to = "crate::events::db::Column::Id",
        on_update = "NoAction",
        on_delete = "NoAction"
    )]
    Event,
    #[sea_orm(
        belongs_to = "crate::person::db::Entity",
        from = "Column::IdPerson",
        to = "crate::person::db::Column::Id",
        on_update = "NoAction",
        on_delete = "NoAction"
    )]
    Person,
}

impl Related<crate::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Event.def()
    }
}

impl Related<crate::person::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Person.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}