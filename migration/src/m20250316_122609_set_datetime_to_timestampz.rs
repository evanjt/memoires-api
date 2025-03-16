use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();

        // Alter `person` table
        db.execute_unprepared(
            "ALTER TABLE public.person 
                ALTER COLUMN created_on TYPE timestamptz USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamptz USING updated_on AT TIME ZONE 'UTC';",
        )
        .await?;

        // Alter `event` table
        db.execute_unprepared(
            "ALTER TABLE public.event 
                ALTER COLUMN start_time TYPE timestamptz USING start_time AT TIME ZONE 'UTC',
                ALTER COLUMN end_time TYPE timestamptz USING end_time AT TIME ZONE 'UTC',
                ALTER COLUMN created_on TYPE timestamptz USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamptz USING updated_on AT TIME ZONE 'UTC';",
        )
        .await?;

        // Alter `person_events` table
        db.execute_unprepared(
            "ALTER TABLE public.person_events 
                ALTER COLUMN created_on TYPE timestamptz USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamptz USING updated_on AT TIME ZONE 'UTC';",
        )
        .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let db = manager.get_connection();

        // Revert `person` table
        db.execute_unprepared(
            "ALTER TABLE public.person 
                ALTER COLUMN created_on TYPE timestamp WITHOUT TIME ZONE USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamp WITHOUT TIME ZONE USING updated_on AT TIME ZONE 'UTC';"
        ).await?;

        // Revert `event` table
        db.execute_unprepared(
            "ALTER TABLE public.event 
                ALTER COLUMN start_time TYPE timestamp WITHOUT TIME ZONE USING start_time AT TIME ZONE 'UTC',
                ALTER COLUMN end_time TYPE timestamp WITHOUT TIME ZONE USING end_time AT TIME ZONE 'UTC',
                ALTER COLUMN created_on TYPE timestamp WITHOUT TIME ZONE USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamp WITHOUT TIME ZONE USING updated_on AT TIME ZONE 'UTC';"
        ).await?;

        // Revert `person_events` table
        db.execute_unprepared(
            "ALTER TABLE public.person_events 
                ALTER COLUMN created_on TYPE timestamp WITHOUT TIME ZONE USING created_on AT TIME ZONE 'UTC',
                ALTER COLUMN updated_on TYPE timestamp WITHOUT TIME ZONE USING updated_on AT TIME ZONE 'UTC';"
        ).await?;

        Ok(())
    }
}
