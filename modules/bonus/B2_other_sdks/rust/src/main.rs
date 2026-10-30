//! Example 1: notes tools in the official Rust SDK. cargo run --manifest-path .../Cargo.toml
//! stdout is exclusively the protocol; writes live only until the process exits.
mod context;
use rmcp::{
    ServerHandler, ServiceExt, handler::server::wrapper::Parameters, schemars, tool, tool_handler,
    tool_router,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Clone, Serialize)]
struct Note {
    id: usize,
    title: String,
    body: String,
    tags: Vec<String>,
}
#[derive(Deserialize, schemars::JsonSchema)]
struct Search {
    #[serde(default)]
    query: String,
}
#[derive(Deserialize, schemars::JsonSchema)]
struct Create {
    title: String,
    body: String,
    #[serde(default)]
    confirmed: bool,
}
#[derive(Deserialize, schemars::JsonSchema)]
struct Tag {
    note_id: usize,
    tag: String,
    #[serde(default)]
    confirmed: bool,
}
#[derive(Clone)]
pub struct Notes {
    notes: Arc<Mutex<Vec<Note>>>,
}

#[tool_router]
impl Notes {
    #[tool(
        description = "Find synthetic notes by title or body. Empty query lists all.",
        annotations(
            read_only_hint = true,
            destructive_hint = false,
            idempotent_hint = true,
            open_world_hint = false
        )
    )]
    fn search_notes(&self, Parameters(input): Parameters<Search>) -> Result<String, String> {
        if input.query.len() > 100 {
            return Err("Query exceeds 100 characters".into());
        }
        let notes = self.notes.lock().map_err(|_| "Notes lock failed")?;
        let found: Vec<_> = notes
            .iter()
            .filter(|n| {
                format!("{} {}", n.title, n.body)
                    .to_lowercase()
                    .contains(&input.query.to_lowercase())
            })
            .collect();
        Ok(serde_json::json!({"result":found}).to_string())
    }
    #[tool(
        description = "Create an ephemeral note after explicit human confirmation.",
        annotations(
            read_only_hint = false,
            destructive_hint = false,
            idempotent_hint = false,
            open_world_hint = false
        )
    )]
    fn create_note(&self, Parameters(input): Parameters<Create>) -> Result<String, String> {
        if !input.confirmed {
            return Err("Confirmation required".into());
        }
        if input.title.is_empty()
            || input.title.len() > 100
            || input.body.is_empty()
            || input.body.len() > 2000
        {
            return Err("Invalid note size".into());
        }
        let mut notes = self.notes.lock().map_err(|_| "Notes lock failed")?;
        let id = notes.len() + 1;
        let result = serde_json::json!({"id":id,"title":input.title}).to_string();
        notes.push(Note {
            id,
            title: input.title,
            body: input.body,
            tags: vec![],
        });
        Ok(result)
    }
    #[tool(
        description = "Add a tag once after confirmation.",
        annotations(
            read_only_hint = false,
            destructive_hint = false,
            idempotent_hint = true,
            open_world_hint = false
        )
    )]
    fn tag_note(&self, Parameters(input): Parameters<Tag>) -> Result<String, String> {
        if !input.confirmed {
            return Err("Confirmation required".into());
        }
        if input.tag.is_empty() || input.tag.len() > 40 {
            return Err("Invalid tag size".into());
        }
        let mut notes = self.notes.lock().map_err(|_| "Notes lock failed")?;
        let n = notes
            .iter_mut()
            .find(|n| n.id == input.note_id)
            .ok_or("Note not found")?;
        if !n.tags.contains(&input.tag) {
            n.tags.push(input.tag);
        }
        Ok(serde_json::json!({"id":n.id,"tags":n.tags}).to_string())
    }
}

#[tool_handler]
impl ServerHandler for Notes {
    fn get_info(&self) -> rmcp::model::ServerConfig {
        rmcp::model::ServerConfig::new(
            rmcp::model::ServerCapabilities::builder()
                .enable_tools()
                .enable_resources()
                .enable_prompts()
                .build(),
        )
    }
    async fn list_resources(
        &self,
        _: Option<rmcp::model::PaginatedRequestParams>,
        _: rmcp::service::RequestContext<rmcp::RoleServer>,
    ) -> Result<rmcp::model::ListResourcesResult, rmcp::ErrorData> {
        Ok(context::resources())
    }
    async fn read_resource(
        &self,
        request: rmcp::model::ReadResourceRequestParams,
        _: rmcp::service::RequestContext<rmcp::RoleServer>,
    ) -> Result<rmcp::model::ReadResourceResponse, rmcp::ErrorData> {
        context::read(&request.uri).map(Into::into)
    }
    async fn list_prompts(
        &self,
        _: Option<rmcp::model::PaginatedRequestParams>,
        _: rmcp::service::RequestContext<rmcp::RoleServer>,
    ) -> Result<rmcp::model::ListPromptsResult, rmcp::ErrorData> {
        Ok(context::prompts())
    }
    async fn get_prompt(
        &self,
        request: rmcp::model::GetPromptRequestParams,
        _: rmcp::service::RequestContext<rmcp::RoleServer>,
    ) -> Result<rmcp::model::GetPromptResponse, rmcp::ErrorData> {
        context::prompt(&request.name).map(Into::into)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let server = Notes {
        notes: Arc::new(Mutex::new(vec![Note {
            id: 1,
            title: "Release handover".into(),
            body: "Review the release checklist.".into(),
            tags: vec!["release".into()],
        }])),
    };
    server
        .serve(rmcp::transport::stdio())
        .await?
        .waiting()
        .await?;
    Ok(())
}
