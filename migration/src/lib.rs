pub use sea_orm_migration::prelude::*;

mod m20220101_000001_create_table;
mod m20250316_122609_set_datetime_to_timestampz;

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20220101_000001_create_table::Migration),
            Box::new(m20250316_122609_set_datetime_to_timestampz::Migration),
        ]
    }
}
