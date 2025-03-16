mod events;
mod person;
mod photo;

use crate::config::Config;
use axum::{extract::DefaultBodyLimit, Router};
use sea_orm::DatabaseConnection;
use utoipa::OpenApi;
use utoipa_axum::router::OpenApiRouter;
use utoipa_scalar::{Scalar, Servable};

// use axum_keycloak_auth::{instance::KeycloakAuthInstance, instance::KeycloakConfig, Url};
// use std::sync::Arc;

pub fn build_router(db: &DatabaseConnection) -> Router {
    #[derive(OpenApi)]
    #[openapi()]
    //     modifiers(&SecurityAddon),
    //     security(
    //         ("bearerAuth" = [])
    //     )
    // )]
    struct ApiDoc;

    // struct SecurityAddon;

    // impl utoipa::Modify for SecurityAddon {
    //     fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
    //         if let Some(components) = openapi.components.as_mut() {
    //             components.add_security_scheme(
    //                 "bearerAuth",
    //                 utoipa::openapi::security::SecurityScheme::Http(
    //                     utoipa::openapi::security::HttpBuilder::new()
    //                         .scheme(utoipa::openapi::security::HttpAuthScheme::Bearer)
    //                         .bearer_format("JWT")
    //                         .build(),
    //                 ),
    //             );
    //         }
    //     }
    // }

    let config: Config = Config::from_env();

    // let keycloak_instance: Arc<KeycloakAuthInstance> = Arc::new(KeycloakAuthInstance::new(
    //     KeycloakConfig::builder()
    //         .server(Url::parse(&config.keycloak_url).unwrap())
    //         .realm(String::from(&config.keycloak_realm))
    //         .build(),
    // ));

    // Build the router with routes from the plots module
    let (router, api) = OpenApiRouter::with_openapi(ApiDoc::openapi())
        .merge(crate::common::views::router(db)) // Root routes
        .nest("/api/events", events::views::router(db, None))
        .nest("/api/perons", person::views::router(db, None))
        .nest("/api/photos", photo::views::router(db, None))
        .nest("/api/gnss", gnss::views::router(db, None))
        .layer(DefaultBodyLimit::max(30 * 1024 * 1024))
        .split_for_parts();

    router.merge(Scalar::with_url("/api/docs", api))
}
