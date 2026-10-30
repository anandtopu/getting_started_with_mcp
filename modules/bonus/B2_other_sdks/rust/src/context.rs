//! Example 2: exact resource routing prevents arbitrary filesystem reads.
use rmcp::model::*;

pub fn resources() -> ListResourcesResult {
    ListResourcesResult {
        resources: vec![Resource::new("lumen://notes/help", "Notes policy")],
        ..Default::default()
    }
}
pub fn read(uri: &str) -> Result<ReadResourceResult, rmcp::ErrorData> {
    if uri != "lumen://notes/help" {
        return Err(rmcp::ErrorData::resource_not_found(
            "Unknown resource",
            None,
        ));
    }
    Ok(ReadResourceResult::new(vec![ResourceContents::text(
        "Review exact note text before creating. Restart clears writes.",
        uri,
    )]))
}

pub fn prompts() -> ListPromptsResult {
    ListPromptsResult {
        prompts: vec![Prompt::new(
            "review_notes",
            Some("Review notes without changing them"),
            None,
        )],
        ..Default::default()
    }
}
pub fn prompt(name: &str) -> Result<GetPromptResult, rmcp::ErrorData> {
    if name != "review_notes" {
        return Err(rmcp::ErrorData::invalid_params("Unknown prompt", None));
    }
    Ok(GetPromptResult::new(vec![PromptMessage::new_text(
        Role::User,
        "Search release notes and cite evidence. Do not write without approval.",
    )]))
}
