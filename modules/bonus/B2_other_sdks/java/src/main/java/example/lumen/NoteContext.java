package example.lumen;

// Example 2: exact resource identity is checked by the server's resource router.
import io.modelcontextprotocol.server.*;
import io.modelcontextprotocol.spec.McpSchema.*;
import java.util.List;

public final class NoteContext {
    public static void register(McpSyncServer server) {
        var resource=Resource.builder("lumen://notes/help","Notes policy").mimeType("text/plain").build();
        server.addResource(new McpServerFeatures.SyncResourceSpecification(resource,(exchange,request)->
            new ReadResourceResult(List.of(new TextResourceContents(request.uri(),"text/plain","Review exact note text before creating. Restart clears writes.")))));
        var prompt = new Prompt("review_notes", "Review notes without changing them", List.of());
        server.addPrompt(new McpServerFeatures.SyncPromptSpecification(prompt, (exchange, request) ->
            new GetPromptResult("Read-only review", List.of(new PromptMessage(Role.USER,
                new TextContent("Search release notes and cite evidence. Do not write without approval."))))));
    }
}
