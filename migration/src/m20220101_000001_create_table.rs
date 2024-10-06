use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Create `person` table
        manager
            .create_table(
                Table::create()
                    .table(Person::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(Person::Id).uuid().primary_key())
                    .col(ColumnDef::new(Person::FirstNames).string().not_null())
                    .col(ColumnDef::new(Person::LastNames).string().not_null())
                    .col(ColumnDef::new(Person::CreatedOn).timestamp().not_null())
                    .col(ColumnDef::new(Person::UpdatedOn).timestamp().not_null())
                    .col(
                        ColumnDef::new(Person::Email)
                            .string()
                            .unique_key()
                            .not_null(),
                    )
                    .to_owned(),
            )
            .await?;

        // Create `event` table
        manager
            .create_table(
                Table::create()
                    .table(Event::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(Event::Id).uuid().primary_key())
                    .col(ColumnDef::new(Event::Title).string().unique_key())
                    .col(ColumnDef::new(Event::Description).text())
                    .col(ColumnDef::new(Event::StartTime).timestamp())
                    .col(ColumnDef::new(Event::EndTime).timestamp().not_null())
                    .col(ColumnDef::new(Event::CreatedOn).timestamp().not_null())
                    .col(ColumnDef::new(Event::UpdatedOn).timestamp().not_null())
                    .to_owned(),
            )
            .await?;

        // Create `person_events` table to associate persons with events
        manager
            .create_table(
                Table::create()
                    .table(PersonEvents::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(PersonEvents::IdPerson).uuid().not_null())
                    .col(ColumnDef::new(PersonEvents::IdEvent).uuid().not_null())
                    .col(
                        ColumnDef::new(PersonEvents::CreatedOn)
                            .timestamp()
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(PersonEvents::UpdatedOn)
                            .timestamp()
                            .not_null(),
                    )
                    .col(
                        ColumnDef::new(PersonEvents::Owner)
                            .boolean()
                            .not_null()
                            .default(false),
                    )
                    .primary_key(
                        Index::create()
                            .col(PersonEvents::IdPerson)
                            .col(PersonEvents::IdEvent),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_person_events_person")
                            .from(PersonEvents::Table, PersonEvents::IdPerson)
                            .to(Person::Table, Person::Id),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk_person_events_event")
                            .from(PersonEvents::Table, PersonEvents::IdEvent)
                            .to(Event::Table, Event::Id),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Drop `person_events` table first due to dependencies
        manager
            .drop_table(Table::drop().table(PersonEvents::Table).to_owned())
            .await?;

        // Drop `event` table
        manager
            .drop_table(Table::drop().table(Event::Table).to_owned())
            .await?;

        // Drop `person` table
        manager
            .drop_table(Table::drop().table(Person::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum Person {
    Table,
    Id,
    FirstNames,
    LastNames,
    Email,
    CreatedOn,
    UpdatedOn,
}

#[derive(DeriveIden)]
enum Event {
    Table,
    Id,
    Title,
    Description,
    StartTime,
    EndTime,
    CreatedOn,
    UpdatedOn,
}

#[derive(DeriveIden)]
enum PersonEvents {
    Table,
    IdPerson,
    IdEvent,
    Owner,
    CreatedOn,
    UpdatedOn,
}
