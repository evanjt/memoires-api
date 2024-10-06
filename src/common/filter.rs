use sea_orm::Condition;
use sea_query::extension::postgres::PgExpr;
use sea_query::{Alias, Expr};
use std::collections::HashMap;
use uuid::Uuid;

pub fn apply_filters(
    filter_str: Option<String>,
    searchable_columns: &[(&str, impl sea_orm::ColumnTrait)],
) -> Condition {
    // Parse the filter string into a HashMap
    let filters: HashMap<String, String> = if let Some(filter) = filter_str {
        serde_json::from_str(&filter).unwrap_or_default()
    } else {
        HashMap::new()
    };

    let mut condition = Condition::all();

    // Check if there is a free-text search ("q") parameter
    if let Some(q_value) = filters.get("q") {
        let mut or_conditions = Condition::any();
        for (_col_name, col) in searchable_columns {
            or_conditions = or_conditions.add(Expr::col(*col).ilike(format!("%{}%", q_value)));
        }
        condition = condition.add(or_conditions);
    } else {
        // Iterate over all filters to build conditions
        for (key, value) in filters {
            let trimmed_value = value.trim().to_string();

            // Check if the value is a UUID
            if let Ok(uuid) = Uuid::parse_str(&trimmed_value) {
                condition = condition.add(Expr::col(Alias::new(&*key)).eq(uuid));
            } else {
                condition = condition
                    .add(Expr::col(Alias::new(&*key)).ilike(format!("%{}%", trimmed_value)));
            }
        }
    }

    condition
}

pub fn parse_range(range_str: Option<String>) -> (u64, u64) {
    if let Some(range) = range_str {
        let range_vec: Vec<u64> = serde_json::from_str(&range).unwrap_or(vec![0, 24]);
        let start = range_vec.get(0).copied().unwrap_or(0);
        let end = range_vec.get(1).copied().unwrap_or(24);
        let limit = end - start + 1;
        (start, limit)
    } else {
        (0, 25)
    }
}
