use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "person")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: Uuid,
    pub first_names: String,
    pub last_names: String,
    #[sea_orm(unique)]
    pub email: String,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "crate::events::db::Entity")]
    Event,
    #[sea_orm(has_many = "crate::person::events::db::Entity")]
    PersonEvents,
}

impl Related<crate::person::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::PersonEvents.def()
    }
}

impl Related<crate::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        crate::person::events::db::Relation::Event.def()
    }
    fn via() -> Option<RelationDef> {
        Some(crate::person::events::db::Relation::Person.def().rev())
    }
}

impl ActiveModelBehavior for ActiveModel {}
