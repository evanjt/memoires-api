use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "photo")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    #[sea_orm(unique)]
    pub uuid: Uuid,
    #[sea_orm(unique)]
    pub original: Uuid,
    pub content_type: String,
    #[sea_orm(unique)]
    pub thumbnail: Option<Uuid>,
    pub camera_time: Option<DateTime>,
    pub gps_time: Option<DateTime>,
    pub validated_time: Option<DateTime>,
    pub checksum_blake2: String,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
