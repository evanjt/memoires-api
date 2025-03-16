use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "person_events")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id_person: Uuid,
    #[sea_orm(primary_key, auto_increment = false)]
    pub id_event: Uuid,
    pub owner: bool, // Add `owner` column
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "crate::routes::events::db::Entity",
        from = "Column::IdEvent",
        to = "crate::routes::events::db::Column::Id",
        on_update = "NoAction",
        on_delete = "NoAction"
    )]
    Event,
    #[sea_orm(
        belongs_to = "crate::routes::person::db::Entity",
        from = "Column::IdPerson",
        to = "crate::routes::person::db::Column::Id",
        on_update = "NoAction",
        on_delete = "NoAction"
    )]
    Person,
}

impl Related<crate::routes::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Event.def()
    }
}

impl Related<crate::routes::person::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Person.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
