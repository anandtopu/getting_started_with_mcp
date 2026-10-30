// Example 2: resource and prompt registration uses attributes, not a second process.
using ModelContextProtocol.Server;
using System.ComponentModel;

[McpServerResourceType]
public static class NotesContext
{
    [McpServerResource(UriTemplate = "lumen://notes/help", Name = "Notes policy", MimeType = "text/plain")]
    public static string Help() => "Review exact note text before creating. Restart clears writes.";
}

[McpServerPromptType]
public static class NotesPrompts
{
    [McpServerPrompt(Name = "review_notes"), Description("Review notes without changing them")]
    public static string Review() => "Search release notes and cite evidence. Do not write without approval.";
}
