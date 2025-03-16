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
    #[sea_orm(has_many = "crate::routes::events::db::Entity")]
    Event,
    #[sea_orm(has_many = "crate::routes::person::events::db::Entity")]
    PersonEvents,
}

impl Related<crate::routes::person::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::PersonEvents.def()
    }
}

impl Related<crate::routes::events::db::Entity> for Entity {
    fn to() -> RelationDef {
        crate::routes::person::events::db::Relation::Event.def()
    }
    fn via() -> Option<RelationDef> {
        Some(
            crate::routes::person::events::db::Relation::Person
                .def()
                .rev(),
        )
    }
}

impl ActiveModelBehavior for ActiveModel {}
