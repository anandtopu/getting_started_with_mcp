// Example 1: real notes server. dotnet run --project modules/bonus/B2_other_sdks/csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Text.Json;

var builder = Host.CreateApplicationBuilder(args);
builder.Logging.AddConsole(options => options.LogToStandardErrorThreshold = LogLevel.Trace);
builder.Services.AddMcpServer().WithStdioServerTransport().WithToolsFromAssembly()
    .WithResourcesFromAssembly().WithPromptsFromAssembly();
await builder.Build().RunAsync();

[McpServerToolType]
public static class Notes
{
    private record Note(int id, string title, string body, List<string> tags);
    private static readonly List<Note> Data = [new(1, "Release handover", "Review the release checklist.", ["release"])];
    private static readonly object Gate = new();

    [McpServerTool(Name = "search_notes", ReadOnly = true, Destructive = false, Idempotent = true, OpenWorld = false), Description("Find synthetic notes by title or body. Empty query lists all.")]
    public static string Search(string query = "")
    {
        if (query.Length > 100) throw new ArgumentException("Query exceeds 100 characters");
        lock (Gate) return JsonSerializer.Serialize(new { result = Data.Where(n => (n.title + " " + n.body).Contains(query, StringComparison.OrdinalIgnoreCase)).ToArray() });
    }

    [McpServerTool(Name = "create_note", ReadOnly = false, Destructive = false, Idempotent = false, OpenWorld = false), Description("Create an ephemeral note after explicit human confirmation.")]
    public static string Create(string title, string body, bool confirmed = false)
    {
        if (!confirmed) throw new ArgumentException("Confirmation required");
        if (title.Length is < 1 or > 100 || body.Length is < 1 or > 2000) throw new ArgumentException("Invalid note size");
        lock (Gate) { var note = new Note(Data.Count + 1, title, body, []); Data.Add(note); return JsonSerializer.Serialize(new { note.id, note.title }); }
    }

    [McpServerTool(Name = "tag_note", ReadOnly = false, Destructive = false, Idempotent = true, OpenWorld = false), Description("Add a tag once after confirmation.")]
    public static string Tag(int note_id, string tag, bool confirmed = false)
    {
        if (!confirmed) throw new ArgumentException("Confirmation required");
        if (tag.Length is < 1 or > 40) throw new ArgumentException("Invalid tag size");
        lock (Gate) { var n = Data.SingleOrDefault(n => n.id == note_id) ?? throw new ArgumentException("Note not found"); if (!n.tags.Contains(tag)) n.tags.Add(tag); return JsonSerializer.Serialize(new { n.id, n.tags }); }
    }
}
